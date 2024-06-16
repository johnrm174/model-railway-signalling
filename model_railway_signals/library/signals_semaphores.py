# --------------------------------------------------------------------------------
# This module is used for creating and managing semaphore signal library objects
# --------------------------------------------------------------------------------
#
# External API - classes and functions (used by the Schematic Editor):
#
#   create_semaphore_signal - Creates a Semaphore signal
#     Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the signal is to be displayed
#       sig_id:int - The ID for the signal - also displayed on the signal button
#       signal_subtype - subtype of the semaphore signal (see above)
#       x:int, y:int - Position of the signal on the canvas (in pixels) 
#       callback - the function to call on signal switched, approached or passed events
#               Note that the callback function returns (item_id, callback type)
#     Optional Parameters:
#       orientation:int - Orientation in degrees (0 or 180) - Default = zero
#       sig_passed_button:bool - Creates a "signal Passed" button - Default = False
#       sig_release_button:bool - Creates an "Approach Release" button - Default = False
#       main_signal:bool - To create a signal arm for the main route - default = True
#                        (Only set this to False when creating an "associated" distant signal
#                        for a situation where a distant arm for the main route is not required)
#       lh1_signal:bool - create a LH1 post with a main (junction) arm - default = False
#       lh2_signal:bool - create a LH2 post with a main (junction) arm - default = False
#       rh1_signal:bool - create a RH1 post with a main (junction) arm - default = False
#       rh2_signal:bool - create a RH2 post with a main (junction) arm - default = False
#       main_subsidary:bool - create a subsidary signal under the "main" signal - default = False
#       lh1_subsidary:bool - create a LH1 post with a subsidary arm - default = False
#       lh2_subsidary:bool - create a LH2 post with a subsidary arm - default = False
#       rh1_subsidary:bool - create a RH1 post with a subsidary arm - default = False
#       rh2_subsidary:bool - create a RH2 post with a subsidary arm - default = False
#       theatre_route_indicator:bool -  Creates a Theatre route indicator - Default = False
#       fully_automatic:bool - Creates a signal without a manual control button - Default = False
#       associated_home:int - Option only valid when creating distant signals
#                        Provide the ID of a previously created home signal (and use the same
#                        x and y coords to create the distant signal on the same post as the home
#                        signal with appropriate "slotting" between the signal arms - Default = False  
#
# Classes and functions used by the other library modules:
#
#   update_semaphore_signal(sig_id:int) - to update the main signal aspect after a change in state
#   update_semaphore_subsidary_arms(sig_id:int) - to update the subsidary aspect after a change in state
#   update_semaphore_route_indication(sig_id:int, route_to_set) - to update the route indication (root arms)
#   trigger_timed_semaphore_signal(sig_id:int, start_delay:int, time_delay:int) - trigger a timed sequence
#
# --------------------------------------------------------------------------------

import logging

from . import common
from . import signals
from . import dcc_control
from . import file_interface

from .signals import semaphore_subtype as semaphore_subtype

# ---------------------------------------------------------------------------------
# Public API Function to create a Semaphore Signal 'object'. The Signal is normally
# set to "NOT CLEAR" = RED unless its fully automatic - when its set to "CLEAR".
# All attributes (that need to be tracked) are stored as a dictionary which is then
# stored in the common dictionary of signals. Note that some elements in the dictionary
# are MANDATORY across all signal types (to allow mixing and matching of signal types)
# ---------------------------------------------------------------------------------
    
def create_semaphore_signal(canvas, sig_id:int,
                            signal_subtype:semaphore_subtype,
                            x:int, y:int, callback,
                            orientation:int=0,
                            sig_passed_button:bool=False,
                            sig_release_button:bool=False,
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
                            fully_automatic:bool=False,
                            associated_home:int=0):
    # Set a default 'tag' to reference the tkinter drawing objects (if creation fails)
    canvas_tag = "signal"+str(sig_id)
    # Get some info about the signal to help validation of the parameters we have been given
    has_subsidary = main_subsidary or lh1_subsidary or lh2_subsidary or rh1_subsidary or rh2_subsidary
    has_route_arms = (lh1_subsidary or lh2_subsidary or rh1_subsidary or rh2_subsidary or
                         lh1_signal or lh2_signal or rh1_signal or rh2_signal )
    # Common validation (common to all signal types) - note we allow sig_ids up to 199 for Semaphore signals
    # as the Editor assignes a sig_id + 100 for secondary distant signals (associated with a home)
    if not isinstance(sig_id, int) or sig_id < 1 or sig_id > 199:
        logging.error("Signal "+str(sig_id)+": create_signal - Signal ID must be an int (1-199)")
    elif signals.signal_exists(sig_id):
        logging.error("Signal "+str(sig_id)+": create_signal - Signal already exists")
    # Type specific validation
    elif signal_subtype not in (semaphore_subtype.home, semaphore_subtype.distant):
        logging.error("Signal "+str(sig_id)+": create_signal - Invalid Signal subtype specified")
    elif has_route_arms and theatre_route_indicator:
        logging.error("Signal "+str(sig_id)+": create_signal - Route Arms AND Theatre Route Indicator specified")
    elif signal_subtype == semaphore_subtype.distant and theatre_route_indicator:
        logging.error("Signal "+str(sig_id)+": create_signal - Distant signals do not support Theatre Route Indicators")
    elif signal_subtype == semaphore_subtype.distant and has_subsidary:
        logging.error("Signal "+str(sig_id)+": create_signal - Distant signals do not support subsidary signals")
    elif signal_subtype == semaphore_subtype.distant and sig_release_button:
        logging.error("Signal "+str(sig_id)+": create_signal - Distant signals do not support Approach Control")
    elif not isinstance(associated_home, int):
        logging.error("Signal "+str(sig_id)+": create_signal - Associated Home ID must be an int")
    elif associated_home > 0 and signal_subtype == semaphore_subtype.home:
        logging.error("Signal "+str(sig_id)+": create_signal - Cannot specify an associated home for a home signal")
    elif associated_home > 0 and not signals.signal_exists(associated_home):
        logging.error("Signal "+str(sig_id)+": create_signal - Associated home "+str(associated_home)+" does not exist")
    elif associated_home > 0 and signals.signals[str(associated_home)]["sigtype"] != signals.signal_type.semaphore:
        logging.error("Signal "+str(sig_id)+": create_signal - Associated home "+str(associated_home)+" is not a semaphore")
    elif associated_home > 0 and signals.signals[str(associated_home)]["subtype"] == semaphore_subtype.distant:
        logging.error("Signal "+str(sig_id)+": create_signal - Associated home "+str(associated_home)+" is not a home signal")
    elif associated_home > 0 and sig_passed_button:
        logging.error("Signal "+str(sig_id)+": create_signal - Cannot create a 'passed' button if associated with another signal")
    elif associated_home == 0 and not main_signal:
        logging.error("Signal "+str(sig_id)+": create_signal - Signal must have a signal arm for the main route")
    else:
        logging.debug("Signal "+str(sig_id)+": Creating library object on the schematic")
        # Create all of the signal elements common to all signal types - note this gives us the 'proper' canvas tag
        canvas_tag = signals.create_common_signal_elements (canvas, sig_id,
                                                signals.signal_type.semaphore,
                                                x, y, orientation, callback,
                                                has_subsidary = has_subsidary,
                                                sig_passed_button = sig_passed_button,
                                                sig_automatic = fully_automatic,
                                                associated_home = associated_home)
        # Work out the offset for the post depending on the combination of signal arms. Note that if
        # this is a distant signal associated with another home signal then we'll use the post offset
        # for the existing signal (as there may be a different combination of home arms specified)
        # This to cater for the situation where not all home arms have an associated distant arm
        if associated_home > 0:
            postoffset = signals.signals[str(associated_home)]["postoffset"]
        elif (not rh2_signal and not rh2_subsidary and not rh1_signal and not rh1_subsidary ):
            if lh2_signal or lh2_subsidary or lh1_signal or lh1_subsidary:
                postoffset = -8
            else:
                postoffset = -15
        elif rh2_signal or rh2_subsidary:
            postoffset = -34
        elif rh1_signal or rh1_subsidary:
            postoffset = -20
        else:
            postoffset = -20
        lh2offset = postoffset-26 
        lh1offset = postoffset-13
        rh1offset = postoffset+13
        rh2offset = postoffset+26 
        # Draw the signal base & signal post (unless this is a distant associated with an existing home signal
        # in which case the signal base & post will already have been drawn when the home signal was created
        # and we therefore only need to add the additional distant arms to the existing posts
        if associated_home == 0:
            line_coords = common.rotate_line(x,y,0,0,0,postoffset,orientation)
            canvas.create_line(line_coords,width=2,fill="snow",tags=canvas_tag)
            line_coords = common.rotate_line(x,y,0,postoffset,+60,postoffset,orientation)
            canvas.create_line(line_coords,width=3,fill="snow",tags=canvas_tag)
            # Draw the rest of the gantry to support other arms as required
            if lh2_signal or lh2_subsidary:
                line_coords = common.rotate_line(x,y,25,postoffset,25,lh2offset,orientation)
                canvas.create_line(line_coords,width=2,fill="snow",tags=canvas_tag)
                if lh2_signal:
                    line_coords = common.rotate_line(x,y,25,lh2offset,55,lh2offset,orientation)
                    canvas.create_line(line_coords,width=2,fill="snow",tags=canvas_tag)
                else:
                    line_coords = common.rotate_line(x,y,25,lh2offset,38,lh2offset,orientation) ##
                    canvas.create_line(line_coords,width=2,fill="snow",tags=canvas_tag)
            if lh1_signal or lh1_subsidary:
                line_coords = common.rotate_line(x,y,25,postoffset,25,lh1offset,orientation)
                canvas.create_line(line_coords,width=2,fill="snow",tags=canvas_tag)
                if lh1_signal:
                    line_coords = common.rotate_line(x,y,25,lh1offset,55,lh1offset,orientation)
                    canvas.create_line(line_coords,width=2,fill="snow",tags=canvas_tag)
                else:
                    line_coords = common.rotate_line(x,y,25,lh1offset,38,lh1offset,orientation) ###
                    canvas.create_line(line_coords,width=2,fill="snow",tags=canvas_tag)
            if rh2_signal or rh2_subsidary:
                line_coords = common.rotate_line(x,y,25,postoffset,25,rh2offset,orientation)
                canvas.create_line(line_coords,width=2,fill="snow",tags=canvas_tag)
                if rh2_signal:
                    line_coords = common.rotate_line(x,y,25,rh2offset,55,rh2offset,orientation)
                    canvas.create_line(line_coords,width=2,fill="snow",tags=canvas_tag)
                else:
                    line_coords = common.rotate_line(x,y,25,rh2offset,38,rh2offset,orientation) ##
                    canvas.create_line(line_coords,width=2,fill="snow",tags=canvas_tag)
            if rh1_signal or rh1_subsidary:
                line_coords = common.rotate_line(x,y,25,postoffset,25,rh1offset,orientation)
                canvas.create_line(line_coords,width=2,fill="snow",tags=canvas_tag)
                if rh1_signal:
                    line_coords = common.rotate_line(x,y,25,rh1offset,55,rh1offset,orientation)
                    canvas.create_line(line_coords,width=2,fill="snow",tags=canvas_tag)
                else:
                    line_coords = common.rotate_line(x,y,25,rh1offset,38,rh1offset,orientation) ##
                    canvas.create_line(line_coords,width=2,fill="snow",tags=canvas_tag)
        # set the colour of the signal arm according to the signal type
        if signal_subtype == semaphore_subtype.distant: arm_colour="yellow"
        else: arm_colour = "red"
        # If this is a distant signal associated with an existing home signal then the distant arms need
        # to be created underneath the main home signal arms - we therefore need to apply a vertical offset
        if associated_home > 0: armoffset = -8
        else: armoffset = 0
        # Draw the signal arm for the main route
        line_coords = common.rotate_line(x,y,55+armoffset,postoffset+3,55+armoffset,postoffset-8,orientation)
        mainsigon = canvas.create_line(line_coords,fill=arm_colour,width=4,tags=canvas_tag)
        line_coords = common.rotate_line(x,y,55+armoffset,postoffset+3,62+armoffset,postoffset-8,orientation)
        mainsigoff = canvas.create_line(line_coords,fill=arm_colour,width=4,state='hidden',tags=canvas_tag)
        # Draw the subsidary arm for the main route
        line_coords = common.rotate_line(x,y,+37,postoffset+3,+37,postoffset-6,orientation)
        mainsubon = canvas.create_line(line_coords,fill=arm_colour,width=3,tags=canvas_tag)
        line_coords = common.rotate_line(x,y,+37,postoffset+3,+42,postoffset-6,orientation)
        mainsuboff = canvas.create_line(line_coords,fill=arm_colour,width=3,state='hidden',tags=canvas_tag)
        # Draw the signal arms for the RH routes
        line_coords = common.rotate_line(x,y,50+armoffset,rh1offset+2,50+armoffset,rh1offset-8,orientation)
        rh1sigon = canvas.create_line(line_coords,fill=arm_colour,width=4,tags=canvas_tag)
        line_coords = common.rotate_line(x,y,50+armoffset,rh1offset+2,57+armoffset,rh1offset-8,orientation)
        rh1sigoff = canvas.create_line(line_coords,fill=arm_colour,width=4,state='hidden',tags=canvas_tag)
        line_coords = common.rotate_line(x,y,50+armoffset,rh2offset+2,50+armoffset,rh2offset-8,orientation)
        rh2sigon = canvas.create_line(line_coords,fill=arm_colour,width=4,tags=canvas_tag)
        line_coords = common.rotate_line(x,y,50+armoffset,rh2offset+2,57+armoffset,rh2offset-8,orientation)
        rh2sigoff = canvas.create_line(line_coords,fill=arm_colour,width=4,state='hidden',tags=canvas_tag)
        # Draw the subsidary arms for the RH routes
        line_coords = common.rotate_line(x,y,+33,rh1offset+2,+33,rh1offset-6,orientation)
        rh1subon = canvas.create_line(line_coords,fill=arm_colour,width=3,tags=canvas_tag)
        line_coords = common.rotate_line(x,y,+33,rh1offset+2,+38,rh1offset-6,orientation)
        rh1suboff = canvas.create_line(line_coords,fill=arm_colour,width=3,state='hidden',tags=canvas_tag)
        line_coords = common.rotate_line(x,y,+33,rh2offset+2,+33,rh2offset-6,orientation)
        rh2subon = canvas.create_line(line_coords,fill=arm_colour,width=3,tags=canvas_tag)
        line_coords = common.rotate_line(x,y,+33,rh2offset+2,+38,rh2offset-6,orientation)
        rh2suboff = canvas.create_line(line_coords,fill=arm_colour,width=3,state='hidden',tags=canvas_tag)
        # Draw the signal arms for the LH routes
        line_coords = common.rotate_line(x,y,50+armoffset,lh1offset+2,50+armoffset,lh1offset-8,orientation)
        lh1sigon = canvas.create_line(line_coords,fill=arm_colour,width=4,tags=canvas_tag)
        line_coords = common.rotate_line(x,y,50+armoffset,lh1offset+2,57+armoffset,lh1offset-8,orientation)
        lh1sigoff = canvas.create_line(line_coords,fill=arm_colour,width=4,state='hidden',tags=canvas_tag)
        line_coords = common.rotate_line(x,y,50+armoffset,lh2offset+2,50+armoffset,lh2offset-8,orientation)
        lh2sigon = canvas.create_line(line_coords,fill=arm_colour,width=4,tags=canvas_tag)
        line_coords = common.rotate_line(x,y,50+armoffset,lh2offset+2,57+armoffset,lh2offset-8,orientation)
        lh2sigoff = canvas.create_line(line_coords,fill=arm_colour,width=4,state='hidden',tags=canvas_tag)
        # Draw the subsidary arms for the LH routes
        line_coords = common.rotate_line(x,y,+33,lh1offset+2,+33,lh1offset-6,orientation)
        lh1subon = canvas.create_line(line_coords,fill=arm_colour,width=3,tags=canvas_tag)
        line_coords = common.rotate_line(x,y,+33,lh1offset+2,+38,lh1offset-6,orientation)
        lh1suboff = canvas.create_line(line_coords,fill=arm_colour,width=3,state='hidden',tags=canvas_tag)
        line_coords = common.rotate_line(x,y,+33,lh2offset+2,+33,lh2offset-6,orientation)
        lh2subon = canvas.create_line(line_coords,fill=arm_colour,width=3,tags=canvas_tag)
        line_coords = common.rotate_line(x,y,+33,lh2offset+2,+38,lh2offset-6,orientation)
        lh2suboff = canvas.create_line(line_coords,fill=arm_colour,width=3,state='hidden',tags=canvas_tag)
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
        # Create the signal elements for a Theatre Route indicator
        signals.create_theatre_route_elements(canvas, sig_id, x, y, xoff=24, yoff=postoffset,
                        orientation=orientation, canvas_tag=canvas_tag, has_theatre=theatre_route_indicator)
        # Create the signal elements to support Approach Control
        signals.create_approach_control_elements(canvas, sig_id, x, y, orientation=orientation,
                                            canvas_tag=canvas_tag, approach_button=sig_release_button)
        # Compile a dictionary of everything we need to track for the signal
        # Note that all MANDATORY attributes are signals_common to ALL signal types
        # All SHARED attributes are signals_common to more than one signal Types
        signals.signals[str(sig_id)]["subtype"]          = signal_subtype         # Type-specific - subtype of the signal (home/distant)
        signals.signals[str(sig_id)]["associatedsignal"] = associated_home        # Type-specific - subtype of the signal (home/distant)
        signals.signals[str(sig_id)]["main_subsidary"]   = main_subsidary         # Type-specific - details of the signal configuration
        signals.signals[str(sig_id)]["lh1_subsidary"]    = lh1_subsidary          # Type-specific - details of the signal configuration
        signals.signals[str(sig_id)]["rh1_subsidary"]    = rh1_subsidary          # Type-specific - details of the signal configuration
        signals.signals[str(sig_id)]["lh2_subsidary"]    = lh2_subsidary          # Type-specific - details of the signal configuration
        signals.signals[str(sig_id)]["rh2_subsidary"]    = rh2_subsidary          # Type-specific - details of the signal configuration
        signals.signals[str(sig_id)]["main_signal"]      = main_signal            # Type-specific - details of the signal configuration
        signals.signals[str(sig_id)]["lh1_signal"]       = lh1_signal             # Type-specific - details of the signal configuration
        signals.signals[str(sig_id)]["rh1_signal"]       = rh1_signal             # Type-specific - details of the signal configuration
        signals.signals[str(sig_id)]["lh2_signal"]       = lh2_signal             # Type-specific - details of the signal configuration
        signals.signals[str(sig_id)]["rh2_signal"]       = rh2_signal             # Type-specific - details of the signal configuration
        signals.signals[str(sig_id)]["postoffset"]       = postoffset             # Type-specific - used for drawing associated distants
        signals.signals[str(sig_id)]["mainsigon"]        = mainsigon              # Type-specific - drawing object
        signals.signals[str(sig_id)]["mainsigoff"]       = mainsigoff             # Type-specific - drawing object
        signals.signals[str(sig_id)]["lh1sigon"]         = lh1sigon               # Type-specific - drawing object
        signals.signals[str(sig_id)]["lh1sigoff"]        = lh1sigoff              # Type-specific - drawing object
        signals.signals[str(sig_id)]["lh2sigon"]         = lh2sigon               # Type-specific - drawing object
        signals.signals[str(sig_id)]["lh2sigoff"]        = lh2sigoff              # Type-specific - drawing object
        signals.signals[str(sig_id)]["rh1sigon"]         = rh1sigon               # Type-specific - drawing object
        signals.signals[str(sig_id)]["rh1sigoff"]        = rh1sigoff              # Type-specific - drawing object
        signals.signals[str(sig_id)]["rh2sigon"]         = rh2sigon               # Type-specific - drawing object
        signals.signals[str(sig_id)]["rh2sigoff"]        = rh2sigoff              # Type-specific - drawing object
        signals.signals[str(sig_id)]["mainsubon"]        = mainsubon              # Type-specific - drawing object
        signals.signals[str(sig_id)]["mainsuboff"]       = mainsuboff             # Type-specific - drawing object
        signals.signals[str(sig_id)]["lh1subon"]         = lh1subon               # Type-specific - drawing object
        signals.signals[str(sig_id)]["lh1suboff"]        = lh1suboff              # Type-specific - drawing object
        signals.signals[str(sig_id)]["lh2subon"]         = lh2subon               # Type-specific - drawing object
        signals.signals[str(sig_id)]["lh2suboff"]        = lh2suboff              # Type-specific - drawing object
        signals.signals[str(sig_id)]["rh1subon"]         = rh1subon               # Type-specific - drawing object
        signals.signals[str(sig_id)]["rh1suboff"]        = rh1suboff              # Type-specific - drawing object
        signals.signals[str(sig_id)]["rh2subon"]         = rh2subon               # Type-specific - drawing object
        signals.signals[str(sig_id)]["rh2suboff"]        = rh2suboff              # Type-specific - drawing object
        # Create the timed sequence class instances for the signal (one per route)
        signals.signals[str(sig_id)]["timedsequence"] = []
        for route in signals.route_type:
            signals.signals[str(sig_id)]["timedsequence"].append(timed_sequence(sig_id,route))
        # if there is an associated signal then we also need to update that signal to refer back to this one
        if associated_home > 0: signals.signals[str(associated_home)]["associatedsignal"] = sig_id
        # Get the initial state for the signal (if layout state has been successfully loaded)
        # Note that each element of 'loaded_state' will be 'None' if no data was loaded
        loaded_state = file_interface.get_initial_item_state("signals",sig_id)
        # Note that for Enum types we load the value - need to turn this back into the Enum
        if loaded_state["routeset"] is not None:
            loaded_state["routeset"] = signals.route_type(loaded_state["routeset"])
        # Set the initial state from the "loaded" state
        if loaded_state["releaseonred"]: signals.set_approach_control(sig_id,release_on_yellow=False)
        if loaded_state["releaseonyel"]: signals.set_approach_control(sig_id,release_on_yellow=True)
        if loaded_state["theatretext"]: signals.update_theatre_route_indication(sig_id,loaded_state["theatretext"])
        if loaded_state["routeset"]: signals.signals[str(sig_id)]["routeset"]=loaded_state["routeset"]
        if loaded_state["override"]: signals.set_signal_override(sig_id)
        # If no state was loaded we still need to toggle fully automatic signals to OFF
        # Note that we also need to Set the signal Arms to the "wrong" initial state so that when they
        # are first updated they get "changed" to the correct aspects and the correct DCC commands sent out
        # We test to see if there is a arm for each route (as the signal may not have one for all the routes)
        if loaded_state["sigclear"] or fully_automatic:
            if (signals.signals[str(sig_id)]["routeset"]==signals.route_type.MAIN
                   and signals.signals[str(sig_id)]["main_signal"]==True ):
                signals.signals[str(sig_id)]["main_signal"] = False
            elif (signals.signals[str(sig_id)]["routeset"]==signals.route_type.LH1
                   and signals.signals[str(sig_id)]["lh1_signal"]==True ):
                signals.signals[str(sig_id)]["lh1_signal"] = False
            elif (signals.signals[str(sig_id)]["routeset"]==signals.route_type.LH2
                   and signals.signals[str(sig_id)]["lh2_signal"]==True ):
                signals.signals[str(sig_id)]["lh2_signal"] = False
            elif (signals.signals[str(sig_id)]["routeset"]==signals.route_type.RH1
                   and signals.signals[str(sig_id)]["rh1_signal"]==True ):
                signals.signals[str(sig_id)]["rh1_signal"] = False
            elif (signals.signals[str(sig_id)]["routeset"]==signals.route_type.RH2
                   and signals.signals[str(sig_id)]["rh2_signal"]==True ):
                signals.signals[str(sig_id)]["rh2_signal"] = False
            signals.toggle_signal(sig_id)
        # Update the signal to show the initial aspect (and send out DCC commands)
        update_semaphore_signal(sig_id)
        # finally Lock the signal if required
        if loaded_state["siglocked"]: signals.lock_signal(sig_id)
        # Set the initial state of the subsidary from the "loaded" state
        # Note that we also need to Set the signal Arms to the "wrong" initial state so that when they
        # are first updated they get "changed" to the correct aspects and the correct DCC commands sent out
        # We test to see if there is a subsidary arm (as the signal may not have one for all the routes)
        if has_subsidary:
            if loaded_state["subclear"]:
                signals.toggle_subsidary(sig_id)
                if (signals.signals[str(sig_id)]["routeset"]==signals.route_type.MAIN
                        and signals.signals[str(sig_id)]["main_subsidary"]==True ):
                    signals.signals[str(sig_id)]["main_subsidary"] = False
                elif (signals.signals[str(sig_id)]["routeset"]==signals.route_type.LH1
                       and signals.signals[str(sig_id)]["lh1_subsidary"]==True ):
                    signals.signals[str(sig_id)]["lh1_subsidary"] = False
                elif (signals.signals[str(sig_id)]["routeset"]==signals.route_type.LH2
                       and signals.signals[str(sig_id)]["lh2_subsidary"]==True ):
                    signals.signals[str(sig_id)]["lh2_subsidary"] = False
                elif (signals.signals[str(sig_id)]["routeset"]==signals.route_type.RH1
                       and signals.signals[str(sig_id)]["rh1_subsidary"]==True ):
                    signals.signals[str(sig_id)]["rh1_subsidary"] = False
                elif (signals.signals[str(sig_id)]["routeset"]==signals.route_type.RH2
                       and signals.signals[str(sig_id)]["rh2_subsidary"]==True ):
                    signals.signals[str(sig_id)]["rh2_subsidary"] = False
            # Update the signal to show the initial aspect (and send out DCC commands)
            update_semaphore_subsidary_arms(sig_id)
            # finally Lock the subsidary if required 
            if loaded_state["sublocked"]: signals.lock_subsidary(sig_id)
        # Publish the initial state to the broker (for other nodes to consume). Note that changes will
        # only be published if the MQTT interface has been configured for publishing updates for this 
        # signal. This allows publish/subscribe to be configured prior to signal creation
        signals.send_mqtt_signal_updated_event(sig_id)
        # Return the canvas_tag for the tkinter drawing objects
    return(canvas_tag)

#-------------------------------------------------------------------
# Internal Function to update the drawing objects for a specified signal Arm
# to represent the state of the signal arm (either ON or OFF). If the signal
# was not created with the specificed signal arm then the state of the signal
# arm will be "None" and the function will have no effect. All changes in the
# signal arm state are logged (together with the additional log message passed
# into the function as to WHY the signal Arm is being changed to its new state
#------------------------------------------------------------------

def update_signal_arm(sig_id, signal_arm, off_element, on_element, set_to_clear, log_message=""):
    # We explicitly test for True or False as "None" signifies the signal arm does not exist
    if set_to_clear and signals.signals[str(sig_id)][signal_arm]==False:
        logging.info("Signal "+str(sig_id)+": Changing \'"+signal_arm+"\' arm to OFF"+log_message)
        signals.signals[str(sig_id)]["canvas"].itemconfigure(signals.signals[str(sig_id)][off_element],state='normal')
        signals.signals[str(sig_id)]["canvas"].itemconfigure(signals.signals[str(sig_id)][on_element],state='hidden')
        dcc_control.update_dcc_signal_element(sig_id,True,element=signal_arm)
        signals.signals[str(sig_id)][signal_arm]=True
    elif not set_to_clear and signals.signals[str(sig_id)][signal_arm]==True:
        logging.info("Signal "+str(sig_id)+": Changing \'"+ signal_arm +"\' arm to ON"+log_message)
        signals.signals[str(sig_id)]["canvas"].itemconfigure(signals.signals[str(sig_id)][off_element],state='hidden')
        signals.signals[str(sig_id)]["canvas"].itemconfigure(signals.signals[str(sig_id)][on_element],state='normal')
        dcc_control.update_dcc_signal_element(sig_id,False,element=signal_arm)
        signals.signals[str(sig_id)][signal_arm]=False
    return()

#-------------------------------------------------------------------
# Helper function to determine if the signal has any diverging route arms
#-------------------------------------------------------------------

def has_diverging_route_arms(sig_id:int):
    has_route_arms = (signals.signals[str(sig_id)]["lh1_subsidary"] is not None or
                      signals.signals[str(sig_id)]["lh2_subsidary"] is not None or
                      signals.signals[str(sig_id)]["rh1_subsidary"] is not None or
                      signals.signals[str(sig_id)]["rh1_subsidary"] is not None or
                      signals.signals[str(sig_id)]["lh1_signal"] is not None or
                      signals.signals[str(sig_id)]["lh2_signal"] is not None or
                      signals.signals[str(sig_id)]["rh1_signal"] is not None or
                      signals.signals[str(sig_id)]["rh2_signal"] is not None )
    return(has_route_arms)

#-------------------------------------------------------------------
# Internal Function to update each of the subsidary signal arms supported by
# a signal to reflect the current state of the subsidary (either ON or OFF)
# and the route set for the signal (i.e the actual subsidary arm that is changed
# will depend on the route that the particular subsidary arm is controlling
# Calls the Update_Signal_Arm function to update the state of each arm
#------------------------------------------------------------------

def update_semaphore_subsidary_arms(sig_id:int, log_message:str=""):
    # We explicitly test for True and False as a state of 'None' signifies the signal was created without a subsidary
    if signals.signals[str(sig_id)]["subclear"] == True:
        # If the route has been set to signals.route_type.NONE then we assume MAIN and change the MAIN arm
        # We also change the MAIN subsidary arm for Home signals without any diverging route arms (main signal or 
        # subsidary signal) to cover the case of a single subsidary signal arm controlling multiple routes
        if ( signals.signals[str(sig_id)]["routeset"] == signals.route_type.MAIN or
             signals.signals[str(sig_id)]["routeset"] == signals.route_type.NONE or
             not has_diverging_route_arms(sig_id)):
            update_signal_arm(sig_id, "main_subsidary", "mainsuboff", "mainsubon", True, log_message)
            update_signal_arm(sig_id, "lh1_subsidary", "lh1suboff", "lh1subon", False, log_message)
            update_signal_arm(sig_id, "lh2_subsidary", "lh2suboff", "lh2subon", False, log_message)
            update_signal_arm(sig_id, "rh1_subsidary", "rh1suboff", "rh1subon", False, log_message)
            update_signal_arm(sig_id, "rh2_subsidary", "rh2suboff", "rh2subon", False, log_message)
        elif signals.signals[str(sig_id)]["routeset"] == signals.route_type.LH1:
            if signals.signals[str(sig_id)]["lh1_subsidary"] is None:
                logging.info("Signal "+str(sig_id)+": No subsidary arm exists for route LH1")
            update_signal_arm(sig_id, "main_subsidary", "mainsuboff", "mainsubon", False, log_message)
            update_signal_arm(sig_id, "lh1_subsidary", "lh1suboff", "lh1subon", True, log_message)
            update_signal_arm(sig_id, "lh2_subsidary", "lh2suboff", "lh2subon", False, log_message)
            update_signal_arm(sig_id, "rh1_subsidary", "rh1suboff", "rh1subon", False, log_message)
            update_signal_arm(sig_id, "rh2_subsidary", "rh2suboff", "rh2subon", False, log_message)
        elif signals.signals[str(sig_id)]["routeset"] == signals.route_type.LH2:
            if signals.signals[str(sig_id)]["lh2_subsidary"] is None:
                logging.info("Signal "+str(sig_id)+": No subsidary arm exists for route LH2")
            update_signal_arm(sig_id, "main_subsidary", "mainsuboff", "mainsubon", False, log_message)
            update_signal_arm(sig_id, "lh1_subsidary", "lh1suboff", "lh1subon", False, log_message)
            update_signal_arm(sig_id, "lh2_subsidary", "lh2suboff", "lh2subon", True, log_message)
            update_signal_arm(sig_id, "rh1_subsidary", "rh1suboff", "rh1subon", False, log_message)
            update_signal_arm(sig_id, "rh2_subsidary", "rh2suboff", "rh2subon", False, log_message)
        elif signals.signals[str(sig_id)]["routeset"] == signals.route_type.RH1:
            if signals.signals[str(sig_id)]["rh1_subsidary"] is None:
                logging.info("Signal "+str(sig_id)+": No subsidary arm exists for route RH1")
            update_signal_arm(sig_id, "main_subsidary", "mainsuboff", "mainsubon", False, log_message)
            update_signal_arm(sig_id, "lh1_subsidary", "lh1suboff", "lh1subon", False, log_message)
            update_signal_arm(sig_id, "lh2_subsidary", "lh2suboff", "lh2subon", False, log_message)
            update_signal_arm(sig_id, "rh1_subsidary", "rh1suboff", "rh1subon", True, log_message)
            update_signal_arm(sig_id, "rh2_subsidary", "rh2suboff", "rh2subon", False, log_message)
        elif signals.signals[str(sig_id)]["routeset"] == signals.route_type.RH2:
            if signals.signals[str(sig_id)]["rh2_subsidary"] is None:
                logging.info("Signal "+str(sig_id)+": No subsidary arm exists for route RH2")
            update_signal_arm(sig_id, "main_subsidary", "mainsuboff", "mainsubon", False, log_message)
            update_signal_arm(sig_id, "lh1_subsidary", "lh1suboff", "lh1subon", False, log_message)
            update_signal_arm(sig_id, "lh2_subsidary", "lh2suboff", "lh2subon", False, log_message)
            update_signal_arm(sig_id, "rh1_subsidary", "rh1suboff", "rh1subon", False, log_message)
            update_signal_arm(sig_id, "rh2_subsidary", "rh2suboff", "rh2subon", True, log_message)
    elif signals.signals[str(sig_id)]["subclear"] == False: 
        # The subsidary signal is at danger
        update_signal_arm(sig_id, "main_subsidary", "mainsuboff", "mainsubon", False, log_message)
        update_signal_arm(sig_id, "lh1_subsidary", "lh1suboff", "lh1subon", False, log_message)
        update_signal_arm(sig_id, "lh2_subsidary", "lh2suboff", "lh2subon", False, log_message)
        update_signal_arm(sig_id, "rh1_subsidary", "rh1suboff", "rh1subon", False, log_message)
        update_signal_arm(sig_id, "rh2_subsidary", "rh2suboff", "rh2subon", False, log_message)
    return ()

# -------------------------------------------------------------------------
# Internal Function to update each of the Main signal arms supported by
# a signal to reflect the current state of the main signal (either ON or OFF)
# and the route set for the signal (i.e the actual  signal arm that is changed
# will depend on the route that the particular signal arm is controlling
# Calls the Update_Signal_Arm function to update the state of each arm
# -------------------------------------------------------------------------

def update_main_signal_arms(sig_id:int, log_message:str=""):
    # When Home/Distant signal is set to PROCEED - the main signal arms will reflect the route
    # Also the case of a home signal associated with a distant signal (i.e on the same post). In
    # this case if the home signal is at DANGER and the distant signal is at CAUTION then the state
    # of the Home signal will be set to caution - in this case we need to set the home arms to OFF
    if (signals.signals[str(sig_id)]["sigstate"] == signals.signal_state_type.PROCEED or
         (signals.signals[str(sig_id)]["sigstate"] == signals.signal_state_type.CAUTION and
           signals.signals[str(sig_id)]["subtype"] == semaphore_subtype.home) ):
        # If the route has been set to signals.route_type.NONE then we assume MAIN and change the MAIN arm
        # We also change the MAIN signal arm for (1) Home signals without any diverging route arms (main signal or 
        # subsidary signal) to cover the case of a single subsidary signal arm controlling multiple routes, and
        # (2) Associated Distant signals where the associated home signal has no diverging route arms
        if ( signals.signals[str(sig_id)]["routeset"] == signals.route_type.MAIN or
             signals.signals[str(sig_id)]["routeset"] == signals.route_type.NONE or
             (not has_diverging_route_arms(sig_id) and not (signals.signals[str(sig_id)]["associatedsignal"] > 0
                      and has_diverging_route_arms(signals.signals[str(sig_id)]["associatedsignal"])))):
            update_signal_arm(sig_id, "main_signal", "mainsigoff", "mainsigon", True, log_message)
            update_signal_arm(sig_id, "lh1_signal", "lh1sigoff", "lh1sigon", False, log_message)
            update_signal_arm(sig_id, "lh2_signal", "lh2sigoff", "lh2sigon", False, log_message)
            update_signal_arm(sig_id, "rh1_signal", "rh1sigoff", "rh1sigon", False, log_message)
            update_signal_arm(sig_id, "rh2_signal", "rh2sigoff", "rh2sigon", False, log_message)
        elif signals.signals[str(sig_id)]["routeset"] == signals.route_type.LH1:
            if signals.signals[str(sig_id)]["lh1_signal"] is None:
                logging.info("Signal "+str(sig_id)+": No main signal arm exists for route LH1")
            update_signal_arm(sig_id, "main_signal", "mainsigoff", "mainsigon", False, log_message)
            update_signal_arm(sig_id, "lh1_signal", "lh1sigoff", "lh1sigon", True, log_message)
            update_signal_arm(sig_id, "lh2_signal", "lh2sigoff", "lh2sigon", False, log_message)
            update_signal_arm(sig_id, "rh1_signal", "rh1sigoff", "rh1sigon", False, log_message)
            update_signal_arm(sig_id, "rh2_signal", "rh2sigoff", "rh2sigon", False, log_message)
        elif signals.signals[str(sig_id)]["routeset"] == signals.route_type.LH2:
            if signals.signals[str(sig_id)]["lh2_signal"] is None:
                logging.info("Signal "+str(sig_id)+": No main signal arm exists for route LH2")
            update_signal_arm(sig_id, "main_signal", "mainsigoff", "mainsigon", False, log_message)
            update_signal_arm(sig_id, "lh1_signal", "lh1sigoff", "lh1sigon", False, log_message)
            update_signal_arm(sig_id, "lh2_signal", "lh2sigoff", "lh2sigon", True, log_message)
            update_signal_arm(sig_id, "rh1_signal", "rh1sigoff", "rh1sigon", False, log_message)
            update_signal_arm(sig_id, "rh2_signal", "rh2sigoff", "rh2sigon", False, log_message)
        elif signals.signals[str(sig_id)]["routeset"] == signals.route_type.RH1:
            if signals.signals[str(sig_id)]["rh1_signal"] is None:
                logging.info("Signal "+str(sig_id)+": No main signal arm exists for route RH1")
            update_signal_arm(sig_id, "main_signal", "mainsigoff", "mainsigon", False, log_message)
            update_signal_arm(sig_id, "lh1_signal", "lh1sigoff", "lh1sigon", False, log_message)
            update_signal_arm(sig_id, "lh2_signal", "lh2sigoff", "lh2sigon", False, log_message)
            update_signal_arm(sig_id, "rh1_signal", "rh1sigoff", "rh1sigon", True, log_message)
            update_signal_arm(sig_id, "rh2_signal", "rh2sigoff", "rh2sigon", False, log_message)
        elif signals.signals[str(sig_id)]["routeset"] == signals.route_type.RH2:
            if signals.signals[str(sig_id)]["rh2_signal"] is None:
                logging.info("Signal "+str(sig_id)+": No main signal arm exists for route RH2")
            update_signal_arm(sig_id, "main_signal", "mainsigoff", "mainsigon", False, log_message)
            update_signal_arm(sig_id, "lh1_signal", "lh1sigoff", "lh1sigon", False, log_message)
            update_signal_arm(sig_id, "lh2_signal", "lh2sigoff", "lh2sigon", False, log_message)
            update_signal_arm(sig_id, "rh1_signal", "rh1sigoff", "rh1sigon", False, log_message)
            update_signal_arm(sig_id, "rh2_signal", "rh2sigoff", "rh2sigon", True, log_message)
    else:
        # Its either a Home signal at DANGER or a Distant Signal at CAUTION
        # In either case - all the main signal arms should be set to ON
        update_signal_arm(sig_id, "main_signal", "mainsigoff", "mainsigon", False, log_message)
        update_signal_arm(sig_id, "lh1_signal", "lh1sigoff", "lh1sigon", False, log_message)
        update_signal_arm(sig_id, "lh2_signal", "lh2sigoff", "lh2sigon", False, log_message)
        update_signal_arm(sig_id, "rh1_signal", "rh1sigoff", "rh1sigon", False, log_message)
        update_signal_arm(sig_id, "rh2_signal", "rh2sigoff", "rh2sigon", False, log_message)
    return()

# -------------------------------------------------------------------------
# Function to Refresh the displayed signal aspect according the signal state
# Also takes into account the state of the signal ahead if one is specified
# to ensure the correct aspect is displayed for 3/4 aspect types and 2 aspect 
# distant signals - e.g. for a 3/4 aspect signal - if the signal ahead is ON
# and this signal is OFF then we want to change it to YELLOW rather than GREEN
# This function assumes the Sig_ID has been validated by the calling programme
# -------------------------------------------------------------------------

def update_semaphore_signal(sig_id:int, updating_associated_signal:bool=False):
    route = signals.signals[str(sig_id)]["routeset"]
    # Get the ID of the associated signal (to make the following code more readable)
    associated_signal = signals.signals[str(sig_id)]["associatedsignal"]
    # Establish what the signal should be displaying based on the state
    if signals.signals[str(sig_id)]["subtype"] == semaphore_subtype.distant:
        if not signals.signals[str(sig_id)]["sigclear"]:
            new_aspect = signals.signal_state_type.CAUTION
            log_message = " (CAUTION) - signal is ON"
        elif signals.signals[str(sig_id)]["override"]:
            new_aspect = signals.signal_state_type.CAUTION
            log_message = " (CAUTION) - signal is OVERRIDDEN"
        elif signals.signals[str(sig_id)]["overcaution"]:
            new_aspect = signals.signal_state_type.CAUTION
            log_message = " (CAUTION) - signal is OVERRIDDEN to CAUTION"
        elif signals.signals[str(sig_id)]["timedsequence"][route.value].sequence_in_progress:
            new_aspect = signals.signal_state_type.CAUTION
            log_message = " (CAUTION) - signal is on a timed sequence"
        elif associated_signal > 0 and signals.signals[str(associated_signal)]["sigstate"] == signals.signal_state_type.DANGER:
            new_aspect = signals.signal_state_type.CAUTION
            log_message = (" (CAUTION) - signal is OFF but slotted with home signal "+str(associated_signal)+" at DANGER")
        else:
            new_aspect = signals.signal_state_type.PROCEED
            log_message = (" (PROCEED) - signal is OFF - route is set to " +
                 str(signals.signals[str(sig_id)]["routeset"]).rpartition('.')[-1] +")")
    else:
        if not signals.signals[str(sig_id)]["sigclear"]:
            new_aspect = signals.signal_state_type.DANGER
            log_message = " (DANGER) - signal is ON"
        elif signals.signals[str(sig_id)]["override"]:
            new_aspect = signals.signal_state_type.DANGER
            log_message = " (DANGER) - signal is OVERRIDDEN"
        elif signals.signals[str(sig_id)]["timedsequence"][route.value].sequence_in_progress:
            new_aspect = signals.signal_state_type.DANGER
            log_message = " (DANGER) - signal is on a timed sequence"
        elif signals.signals[str(sig_id)]["releaseonred"]:
            new_aspect = signals.signal_state_type.DANGER
            log_message = " (DANGER) - signal is subject to \'release on red\' approach control"
        elif associated_signal > 0 and signals.signals[str(associated_signal)]["sigstate"] == signals.signal_state_type.CAUTION:
            new_aspect = signals.signal_state_type.CAUTION
            log_message = (" (CAUTION) - signal is OFF but associated distant "+str(associated_signal)+" is at CAUTION")
        else:
            new_aspect = signals.signal_state_type.PROCEED
            log_message = (" (PROCEED) - signal is OFF - route is set to " +
                 str(signals.signals[str(sig_id)]["routeset"]).rpartition('.')[-1] +")")
    current_aspect = signals.signals[str(sig_id)]["sigstate"]
    # Now refresh the displayed aspect (passing in the log message to be displayed) if the aspect has changed
    if new_aspect != current_aspect:
        signals.signals[str(sig_id)]["sigstate"] = new_aspect
        update_main_signal_arms(sig_id, log_message)
        # If this signal is an associated with another signal then we also need to refresh the other signal
        # Associated distant signals need to be updated as they are "slotted" with the home signal - i.e. if the
        # home signal is set to DANGER then the distant signal (on the same arm) should show CAUTION
        # Associated Home signals need to be updated as the internal state of home signals relies on the state of
        # the distant signal and the home signal (i.e. Home is OFF but distant is ON - State is therefore CAUTION
        # We set a flag for the recursive call so we don't end up in a circular recursion
        if associated_signal > 0 and not updating_associated_signal:
            update_semaphore_signal(associated_signal, updating_associated_signal=True)
        # Call the common function to update the theatre route indicator elements
        # (if the signal has a theatre route indicator - otherwise no effect)
        signals.enable_disable_theatre_route_indication(sig_id)
        # Publish the signal changes to the broker (for other nodes to consume). Note that state changes will only
        # be published if the MQTT interface has been successfully configured for publishing updates for this signal
        signals.send_mqtt_signal_updated_event(sig_id)
        # For associated distant signals we need to take into account the state of both the home and distant signals
        # to set the correct "state" for the associated home/distant signal - and we will only know this state once
        # both home and distant signals have been updated (to take into account any "slotting")
        if ( signals.signals[str(sig_id)]["subtype"] == semaphore_subtype.home and associated_signal > 0 and
             signals.signals[str(sig_id)]["sigstate"] == signals.signal_state_type.CAUTION and
             signals.signals[str(associated_signal)]["sigstate"] == signals.signal_state_type.PROCEED ):
            logging.info("Signal "+str(sig_id)+": Updating signal state to PROCEED - associated (slotted) distant is now OFF")
            signals.signals[str(sig_id)]["sigstate"] = signals.signal_state_type.PROCEED
    return()

# -------------------------------------------------------------------------
# Function to set (and update) the route indication for the signal
# Calls the internal functions to update the route feathers and the
# theatre route indication. This Function assumes the Sig_ID has
# already been validated by the calling programme
# -------------------------------------------------------------------------

def update_semaphore_route_indication(sig_id:int, route_to_set):
    # Only update the respective route indication if the route has been changed and has actively
    # been set (a route of 'NONE' signifies that the particular route indication isn't used) 
    if route_to_set is not None and signals.signals[str(sig_id)]["routeset"] != route_to_set:
        logging.info("Signal "+str(sig_id)+": Setting semaphore route to "+str(route_to_set).rpartition('.')[-1])
        signals.signals[str(sig_id)]["routeset"] = route_to_set
        # Refresh the signal drawing objects (which will also send the DCC commands to change the arms accordingly)
        # Log messages will also be generated for each change - so we don't need lo log anything extra here
        update_main_signal_arms(sig_id," (route has been changed to "+str(route_to_set).rpartition('.')[-1]+")")
        # Also update the subsidary aspects for route changes (as these may be represented by different subsidary arms)
        update_semaphore_subsidary_arms(sig_id," (route has been changed to "+str(route_to_set).rpartition('.')[-1]+")")
        # If this is a home signal with an associated distant signal then we also need to set the route for
        # the distant signal as it is effectively on the same post and "slotted" with the home signal
        # Get the ID of the associated signal (to make the following code more readable)
        associated_signal = signals.signals[str(sig_id)]["associatedsignal"]
        if signals.signals[str(sig_id)]["subtype"] == semaphore_subtype.home and associated_signal > 0:
            update_semaphore_route_indication (associated_signal,route_to_set)
        # Refresh the signal aspect (a catch-all to ensure the signal displays the correct aspect)
        # in case the signal is in the middle of a timed sequence for the old route or the new route
        update_semaphore_signal(sig_id)
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
        if self.sequence_abort_flag or not signals.signal_exists(self.sig_id):
            self.sequence_in_progress = False
        else:
            self.sequence_in_progress = True
            # For a start delay of zero we assume the intention is not to make a callback (on the basis
            # that the user has triggered the timed signal in the first place). For start delays > 0 the 
            # sequence is initiated after the specified delay and this will trigger a callback
            # Note that we only change the aspect and generate the callback if the same route is set
            if signals.signals[str(self.sig_id)]["routeset"] == self.sig_route:
                if self.start_delay > 0:                 
                    logging.info("Signal "+str(self.sig_id)+": Timed Signal - Signal Passed Event **************************")
                    update_semaphore_signal(self.sig_id)
                    # Publish the signal passed event via the mqtt interface. Note that the event will only be published if the
                    # mqtt interface has been successfully configured and the signal has been set to publish passed events
                    signals.publish_signal_passed_event(self.sig_id)
                    signals.signals[str(self.sig_id)]["extcallback"] (self.sig_id,signals.signal_callback_type.sig_passed)
                else:
                    update_semaphore_signal(self.sig_id)
            # We need to schedule the sequence completion (i.e. back to clear
            common.root_window.after(self.time_delay*1000,lambda:self.timed_signal_sequence_end())

    def timed_signal_sequence_end(self):
        # We've finished - Set the signal back to its "normal" condition
        self.sequence_in_progress = False
        if signals.signal_exists(self.sig_id):
            logging.info("Signal "+str(self.sig_id)+": Timed Signal - Signal Updated Event *************************")
            update_semaphore_signal(self.sig_id)
            signals.signals[str(self.sig_id)]["extcallback"] (self.sig_id, signals.signal_callback_type.sig_updated)

# -------------------------------------------------------------------------
# Function to initiate a timed signal sequence - setting the signal initially to ON
# and then returning to OFF (assuming the signal is clear and nor overridden) after
# the specified time delay. Intended for automation of 'exit' signals on a layout.
# The start_delay is the initial delay (in seconds) before the signal is set to ON
# and the time_delay is the delay before the signal returns to OFF. A 'sig_passed'
# callback event will be generated when the signal is set to ON if if a start delay
# is specified. When returning to OFF, a 'sig_updated' callback event will be generated.
# -------------------------------------------------------------------------

def trigger_timed_semaphore_signal(sig_id:int, start_delay:int, time_delay:int):
    
    def delayed_sequence_start(sig_id:int, sig_route):
        if signals.signal_exists(sig_id) and not common.shutdown_initiated:
            signals.signals[str(sig_id)]["timedsequence"][route.value].start()
            
    # Don't initiate a timed signal sequence if a shutdown has already been initiated
    if common.shutdown_initiated:
        logging.warning("Signal "+str(sig_id)+": Timed Signal - Shutdown initiated - not triggering timed signal")
    else:
        # Abort any timed signal sequences already in progess
        route = signals.signals[str(sig_id)]["routeset"]
        signals.signals[str(sig_id)]["timedsequence"][route.value].abort()
        # Create a new instance of the time signal class - this should have the effect of "destroying"
        # the old instance when it goes out of scope, leaving us with the newly created instance
        signals.signals[str(sig_id)]["timedsequence"][route.value] = timed_sequence(sig_id, route, start_delay, time_delay)
        # Schedule the start of the sequence (i.e. signal to danger) if the start delay is greater than zero
        # Otherwise initiate the sequence straight away (so the signal state is updated immediately)
        if start_delay > 0:
            common.root_window.after(start_delay*1000,lambda:delayed_sequence_start(sig_id,route))
        else:
            signals.signals[str(sig_id)]["timedsequence"][route.value].start()
    return()

###############################################################################
