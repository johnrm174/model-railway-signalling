# --------------------------------------------------------------------------------
# This module is used for creating and managing Track Occupancy objects (sections)
#
# The following functions are designed to be called by external modules
#
# create_section - Creates a section object
#   Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the section is to be displayed
#       section_id:int - The ID to be used for the section 
#       x:int, y:int - Position of the point on the canvas (in pixels)
#   Optional Parameters:
#       section_callback - The function to call if the section is manually toggled - default: null
#       label - The label to display on the section when occupied - default: "Train On Line"
#
# section_occupied - Returns the current state of the section (True/False)
#   Mandatory Parameters:
#       section_id:int - The ID of the section
#
# set_section_occupied - Sets the specified section to "occupied"
#   Mandatory Parameters:
#       section_id:int - The ID of the section
#
# clear_section_occupied - Sets the specified section to "clear"
#   Mandatory Parameters:
#       section_id:int - The ID of the section
#
# --------------------------------------------------------------------------------

# change the way we import depending on whether we are running locally or not
# We do this so we can run the python code checker over the module when developing
#import common
from . import common

from tkinter import *
import tkinter.font
import enum

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
# Internal function to flip the state of the section. This Will SET/UNSET
# the section and initiate an external callback if one is specified
# -------------------------------------------------------------------------

def toggle_section (section_id:int, ext_callback=section_null):
    global sections # the dictionary of sections
    # Validate the section exists 
    if not section_exists(section_id):
        print ("ERROR: toggle_section - Section "+str(section_id)+" does not exist")
    else:
        # get the section that we are interested in
        section = sections[str(section_id)]
        if section["occupied"] == True:  # section is on
            section["occupied"] = False
            section["button1"].config(relief="raised", bg="grey", fg="grey",
                            activebackground="grey", activeforeground="grey")
        else:  # section is off
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
    # also uses fontsize, xpadding, ypadding imported from "common"

    # Verify that a section with the same ID does not already exist
    if section_exists(section_id):
        print ("ERROR: create_section - section ID "+str(section_id)+" already exists")
    elif section_id < 1:
        print ("ERROR: create_section - section ID must be greater than zero")
    else: # we're good to go on and create the section
        
        # set the font size for the buttons
        myfont = tkinter.font.Font(size = common.fontsize)

        # Create the button objects and their callbacks
        button1 = Button (canvas,text=label, state="normal",
                    padx=common.xpadding, pady=common.ypadding,
                    relief="raised", font=myfont,
                    bg="grey", fg="grey", activebackground="grey", activeforeground="grey",
                    command = lambda:toggle_section(section_id,section_callback))

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
    # Validate the section exists
    if not section_exists(section_id):
        print ("ERROR: section_occupied - section "+str(section_id)+" does not exist")
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
    # Validate the section exists
    if not section_exists(section_id):
        print ("ERROR: set_section_occupied - section "+str(section_id)+" does not exist")
    elif not section_occupied(section_id):
        toggle_section(section_id)
    return()

def clear_section_occupied (section_id:int):
    # Validate the section exists
    if not section_exists(section_id):
        print ("ERROR: clear_section_occupied - section "+str(section_id)+" does not exist")
    if section_occupied(section_id,):
        toggle_section(section_id)
    return()

###############################################################################

