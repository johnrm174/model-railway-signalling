# --------------------------------------------------------------------------------
# This module is used for creating and managing Track Occupancy objects (sections)
#
# section_callback_type (tells the calling program what has triggered the callback):
#     section_callback_type.section_switched - The section has been toggled (occupied/clear) by the user
# 
# create_section - Creates a Track Occupancy section object
#   Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the section is to be displayed
#       section_id:int - The ID to be used for the section 
#       x:int, y:int - Position of the section on the canvas (in pixels)
#   Optional Parameters:
#       section_callback - The function to call if the section is manually toggled - default: null
#                         Note that the callback function returns (item_id, callback type)
#       label - The label to display on the section when occupied - default: "Train On Line"
# 
# section_occupied (section_id)- Returns the current state of the section (True=Occupied, False=Clear)
# 
# set_section_occupied (section_id) - Sets the specified section to "occupied"
# 
# clear_section_occupied (section_id)- Sets the specified section to "clear"
#
# --------------------------------------------------------------------------------

from . import common
from tkinter import *
import enum
import logging

# -------------------------------------------------------------------------
# Classes used by external functions when calling the create_point function
# -------------------------------------------------------------------------
    
# Define the different callbacks types for the section
class section_callback_type(enum.Enum):
    section_switched = 21   # The section has been manually switched by the user
    
# -------------------------------------------------------------------------
# sections are to be added to a global dictionary when created
# -------------------------------------------------------------------------

# Define an empty dictionary 
sections: dict = {}

# -------------------------------------------------------------------------
# The default "External" callback for the section buttons
# Used if this is not specified when the section is created
# -------------------------------------------------------------------------

def null_callback(section_id:int, callback_type):
    return(section_id, callback_type)

# -------------------------------------------------------------------------
# Internal Function to check if a section exists in the list of section
# Used in Most externally-called functions to validate the section ID
# -------------------------------------------------------------------------

def section_exists(section_id:int):
    return (str(section_id) in sections.keys() )

# -------------------------------------------------------------------------
# Callback for processing Button presses (manual toggling of Track Sections
# -------------------------------------------------------------------------

def section_button_event (section_id:int):
    global logging
    logging.info ("Section "+str(section_id)+": Track Section Toggled *****************************")
    toggle_section(section_id)
    sections[str(section_id)]["extcallback"] (section_id,section_callback_type.section_switched)
    return ()

# -------------------------------------------------------------------------
# Internal function to flip the state of the section. This Will SET/UNSET
# the section and initiate an external callback if one is specified
# -------------------------------------------------------------------------

def toggle_section (section_id:int):
    
    global sections # the dictionary of sections
    global logging
    
    if sections[str(section_id)]["occupied"]:
        # section is on
        logging.info ("Section "+str(section_id)+": Changing to CLEAR")
        sections[str(section_id)]["occupied"] = False
        sections[str(section_id)]["button1"].config(relief="raised", bg="grey", fg="grey40",
                                            activebackground="grey", activeforeground="grey40")
    else:
        # section is off
        logging.info ("Section "+str(section_id)+": Changing to OCCUPIED")
        sections[str(section_id)]["occupied"] = True
        sections[str(section_id)]["button1"].config(relief="sunken", bg="black",fg="white",
                                            activebackground="black", activeforeground="white")
    return()

# -------------------------------------------------------------------------
# Externally called function to create a section (drawing objects + state)
# All attributes (that need to be tracked) are stored as a dictionary
# This is then added to a dictionary of sections for later reference
# -------------------------------------------------------------------------

def create_section (canvas, section_id:int, x:int, y:int,
                    section_callback = null_callback,
                    label:str = "Train On Line"):
    
    global sections # the dictionary of sections
    global logging
    # also uses fontsize, xpadding, ypadding imported from "common"

    logging.info ("Section "+str(section_id)+": Creating Track Occupancy Section")
    # Verify that a section with the same ID does not already exist
    if section_exists(section_id):
        logging.error ("Section "+str(section_id)+": Section already exists")
    elif section_id < 1:
        logging.error ("Section "+str(section_id)+": Section ID must be greater than zero")
    else:
        
        # Create the button objects and their callbacks
        section_button = Button (canvas, text=label, state="normal", relief="raised",
                    padx=common.xpadding, pady=common.ypadding, font=('Ariel',8,"normal"),
                    bg="grey", fg="grey40", activebackground="grey", activeforeground="grey40",
                    command = lambda:section_button_event(section_id))
        canvas.create_window (x,y,window=section_button) 

        # Compile a dictionary of everything we need to track
        sections[str(section_id)] = {"canvas" : canvas,                   # canvas object
                                     "button1" : section_button,          # drawing object
                                     "extcallback" : section_callback,    # External callback to make
                                     "occupied" : False }                 # Current state

    return()

# -------------------------------------------------------------------------
# Externally called function to Return the current state of the section
# -------------------------------------------------------------------------

def section_occupied (section_id:int):
    
    global sections # the dictionary of sections
    global logging
    
    # Validate the section exists
    if not section_exists(section_id):
        logging.error ("Section "+str(section_id)+": section_occupied - Section does not exist")
        occupied = False
    else:   
        occupied = sections[str(section_id)]["occupied"]
    return(occupied)

# -------------------------------------------------------------------------
# Externally called functions to Set and Clear a section
# -------------------------------------------------------------------------

def set_section_occupied (section_id:int):
    
    global logging
    
    # Validate the section exists
    if not section_exists(section_id):
        logging.error ("Section "+str(section_id)+": set_section_occupied - Section does not exist")
    elif not section_occupied(section_id):
        toggle_section(section_id)
    return()

def clear_section_occupied (section_id:int):
    # Validate the section exists
    if not section_exists(section_id):
        logging.error ("Section "+str(section_id)+": clear_section_occupied - Section does not exist")
    elif section_occupied(section_id):
        toggle_section(section_id)
    return()

###############################################################################

