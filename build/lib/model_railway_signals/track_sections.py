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

# change the way we import depending on whether we are running locally or not
# We do this so we can run the python code checker over the module when developing
#import common
from . import common

from tkinter import *
import tkinter.font
import enum
import logging

# -------------------------------------------------------------------------
# Classes used by external functions when calling the create_point function
# -------------------------------------------------------------------------
    
# Define the different callbacks types for the section
class section_callback_type(enum.Enum):
    null_event = 20
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

def section_null(section_id, section_callback = section_callback_type.null_event):
    return(section_id, section_callback)

# -------------------------------------------------------------------------
# Internal Function to check if a section exists in the list of section
# Used in Most externally-called functions to validate the section ID
# -------------------------------------------------------------------------

def section_exists(section_id):
    return (str(section_id) in sections.keys() )

# -------------------------------------------------------------------------
# Callback for processing Button presses (manual toggling of Track Sections
# -------------------------------------------------------------------------

def section_button_event (section_id:int,external_callback):
    global logging
    logging.info ("Section "+str(section_id)+": Track Section Manual Update *****************************")
    toggle_section(section_id,external_callback)
    return ()

# -------------------------------------------------------------------------
# Internal function to flip the state of the section. This Will SET/UNSET
# the section and initiate an external callback if one is specified
# -------------------------------------------------------------------------

def toggle_section (section_id:int, ext_callback=section_null):
    
    global sections # the dictionary of sections
    global logging
    
    # get the section that we are interested in
    section = sections[str(section_id)]
    if section["occupied"] == True:  # section is on
        logging.info ("Section "+str(section_id)+": Changing to CLEAR")
        section["occupied"] = False
        section["button1"].config(relief="raised", bg="grey", fg="grey",
                        activebackground="grey", activeforeground="grey")
    else:  # section is off
        logging.info ("Section "+str(section_id)+": Changing to OCCUPIED")
        section["occupied"] = True
        section["button1"].config(relief="sunken", bg="black",fg="white",
                        activebackground="black", activeforeground="white")
    # update the dictionary of sections with the new state  
    sections[str(section_id)] = section;
    # Now make the external callback
    ext_callback(section_id,section_callback_type.section_switched)
    return()

# -------------------------------------------------------------------------
# Externally called function to create a section (drawing objects + state)
# All attributes (that need to be tracked) are stored as a dictionary
# This is then added to a dictionary of sections for later reference
# -------------------------------------------------------------------------

def create_section (canvas, section_id:int, x:int, y:int,
                    section_callback = section_null,
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
    else: # we're good to go on and create the section
        
        # set the font size for the buttons
        myfont = tkinter.font.Font(size = common.fontsize)

        # Create the button objects and their callbacks
        button1 = Button (canvas,text=label, state="normal",
                    padx=common.xpadding, pady=common.ypadding,
                    relief="raised", font=myfont,
                    bg="grey", fg="grey", activebackground="grey", activeforeground="grey",
                    command = lambda:section_button_event(section_id,section_callback))

        # Create some drawing objects (depending on section type)
        canvas.create_window (x,y,window=button1) 

        # Compile a dictionary of everything we need to track
        new_section = {"canvas" : canvas,               # canvas object
                      "button1" : button1,              # drawing object
                      "occupied" : False }

        # Add the new section to the dictionary of sections
        sections[str(section_id)] = new_section 
        
    return()

# -------------------------------------------------------------------------
# Externally called function to Return the current state of the section
# -------------------------------------------------------------------------

def section_occupied (section_id:int):
    
    global sections # the dictionary of sections
    global logging
    
    # Validate the section exists
    if not section_exists(section_id):
        logging.error ("Section "+str(section_id)+": Section does not exist")
        occupied = False
    else:   
        # get the section that we are interested in
        section = sections[str(section_id)]
        occupied = section["occupied"]
    return(occupied)

# -------------------------------------------------------------------------
# Externally called functions to Set and Clear a section
# -------------------------------------------------------------------------

def set_section_occupied (section_id:int):
    
    global logging
    
    # Validate the section exists
    if not section_exists(section_id):
        logging.error ("Section "+str(section_id)+": Section to set to Occupied does not exist")
    elif not section_occupied(section_id):
        toggle_section(section_id)
    return()

def clear_section_occupied (section_id:int):
    # Validate the section exists
    if not section_exists(section_id):
        logging.error ("Section "+str(section_id)+": Section to set to Clear does not exist")
    if section_occupied(section_id,):
        toggle_section(section_id)
    return()

###############################################################################

