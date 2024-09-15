#---------------------------------------------------------------------------------------------
# This module is used for creating and managing Line objects on the schematic
# --------------------------------------------------------------------------------------------
#
# Public types and functions:
# 
#   create_line - Creates a button object
#     Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the Line is to be displayed
#       line_id:int - The ID to be used for the Line object 
#       x1:int, y1:int - Position of 'End 1' of the line (in pixels)
#       x2:int, y2:int -  Position of 'End 1' of the line (in pixels)
#     Optional parameters:
#       colour:int - The colour of the line (default Black)
#       arrow_type:[int,int,int] - The line end type to be displayed (default [0,0,0])
#       arrow_ends:int - how the arrow_types are to be applied -  0=none, 1=start, 2=end, 3=both (default 0)
#       selected:bool:int - Set to True to create the line as "selected" (default False)
#
#   line_exists(line_id:int) - returns true if the Button object 'exists' on the schematic
#
#   delete_line(line_id:int) - Delete the library object from the schematic
#
#   set_line_colour(line_id:int, colour:str) - change the colour of a line
#
#   reset_line_colour(line_id:int) - reset the colour of a line back to default
# 
#---------------------------------------------------------------------------------------------

import logging
import tkinter as Tk
import math

#---------------------------------------------------------------------------------------------
# Line objects are to be added to a global dictionary when created
#---------------------------------------------------------------------------------------------

lines: dict = {}
                                                            
#---------------------------------------------------------------------------------------------
# API Function to check if a Line Object exists in the list of Lines
# Used in most externally-called functions to validate the Line ID
#---------------------------------------------------------------------------------------------

def line_exists(line_id:int):
    if not isinstance(line_id, int):
        logging.error("Line "+str(line_id)+": line_exists - Line ID must be an int")
        line_exists = False
    else:
        line_exists = str(line_id) in lines.keys()
    return(line_exists)

#---------------------------------------------------------------------------------------------
# Public API function to create a Line object (drawing objects)
#---------------------------------------------------------------------------------------------

def create_line (canvas, line_id:int, x1:int, y1:int, x2:int, y2:int, colour:str="black",
                  arrow_type:list=[0,0,0], arrow_ends:int=0, selected:bool=False):
    global lines
    # Set a unique 'tag' to reference the tkinter drawing objects
    canvas_tag = "line"+str(line_id)
    # Create an aditional tag for the line "selection" indication
    selected_tag = "line"+str(line_id)+"selected"
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(line_id, int) or line_id < 1 or line_id > 999:
        logging.error("Line "+str(line_id)+": create_line - Line ID must be an int (1-999)")
    elif line_exists(line_id):
        logging.error("Line "+str(line_id)+": create_line - Line ID already exists")
    else:
        logging.debug("Line "+str(line_id)+": Creating Line on the Canvas")
        # Draw the line (with arrow heads if these are selected). An arrow_type configuration
        # of [1,1,1] is used to select 'end stops' over 'arrows'. Note that we store this
        # configuration as a list rather than the tuple needed by the tkinter create_line
        # function so it is serialisable to json for save and load.
        if arrow_type != [0,0,0] and arrow_type != [1,1,1] and arrow_ends == 1:
            line_object = canvas.create_line(x1, y1, x2, y2, fill=colour, width=3,
                            arrow=Tk.FIRST, arrowshape=tuple(arrow_type), tags=canvas_tag)
        elif arrow_type != [0,0,0] and arrow_type != [1,1,1] and arrow_ends == 2:
            line_object = canvas.create_line(x1, y1, x2, y2, fill=colour,width=3,
                            arrow=Tk.LAST, arrowshape=tuple(arrow_type), tags=canvas_tag)
        elif arrow_type != [0,0,0] and arrow_type != [1,1,1] and arrow_ends == 3:
            line_object = canvas.create_line(x1, y1, x2, y2, fill=colour, width=3,
                            arrow=Tk.BOTH, arrowshape=tuple(arrow_type), tags=canvas_tag)
        else:
            line_object = canvas.create_line(x1, y1, x2, y2, fill=colour, width=3, tags=canvas_tag)
        # Draw the line end selection circles (i.e displayed when line selected)
        if selected: state="normal"
        else: state = "hidden"
        end1_object = canvas.create_oval(x1-5, y1-5, x1+5, y1+5, tags=(canvas_tag, selected_tag), state=state)
        end2_object = canvas.create_oval(x2-5, y2-5, x2+5, y2+5, tags=(canvas_tag, selected_tag), state=state)
        # Draw the line 'end stops' - these are only displayed if selected (otherwise hidden)
        # An arrow_type configuration of [1,1,1] is used to select 'end stops' over 'arrows'
        if arrow_type == [1,1,1] and arrow_ends == 1: stop1, stop2 = "normal", "hidden"
        elif arrow_type == [1,1,1] and arrow_ends == 2: stop1, stop2 = "hidden", "normal"
        elif arrow_type == [1,1,1] and arrow_ends == 3: stop1, stop2 = "normal", "normal"
        else: stop1, stop2 = "hidden", "hidden"
        dx, dy = get_endstop_offsets(x1, y1, x2, y2)
        stop1_object = canvas.create_line(x1+dx, y1+dy, x1-dx, y1-dy, fill=colour, width=3, tags=canvas_tag, state=stop1)
        stop2_object = canvas.create_line(x2+dx, y2+dy, x2-dx, y2-dy, fill=colour, width=3, tags=canvas_tag, state=stop2)
        # Compile a dictionary of everything we need to track
        lines[str(line_id)] = {}
        lines[str(line_id)]["canvas"] = canvas                  # Tkinter canvas object
        lines[str(line_id)]["colour"] = colour                  # Default colour for the line
        lines[str(line_id)]["line"] = line_object               # Reference to the Tkinter drawing object
        lines[str(line_id)]["end1"] = end1_object               # Reference to the Tkinter drawing object
        lines[str(line_id)]["end2"] = end2_object               # Reference to the Tkinter drawing object
        lines[str(line_id)]["stop1"] = stop1_object             # Reference to the Tkinter drawing object
        lines[str(line_id)]["stop2"] = stop2_object             # Reference to the Tkinter drawing object
        lines[str(line_id)]["tags"] = canvas_tag                # Canvas Tag for ALL drawing objects
    # Return the canvas tag references
    return(canvas_tag, selected_tag)

#------------------------------------------------------------------------------------
# Internal Function to get the x and y deltas for a line 'end stop' - a short line 
# perpendicular to the main line - normally used to represent a buffer stop
# Used by the create_line function and the move_line_end functions
#------------------------------------------------------------------------------------

def get_endstop_offsets(x1, y1, x2, y2):
    if x2 != x1: slope = (y2-y1)/(x2-x1)
    else: slope = 1000000
    dy = math.sqrt(9**2/(slope**2+1))
    dx = -slope*dy
    return(dx, dy)

#------------------------------------------------------------------------------------
# API functions to move a line end by the specified x and y deltas
#------------------------------------------------------------------------------------

def move_line_end_1(line_id:int, xdiff:int, ydiff:int):
    if not isinstance(line_id, int):
        logging.error("Line "+str(line_id)+": move_line_end_1 - Line ID must be an int")
    elif not line_exists(line_id):
        logging.error("Line "+str(line_id)+": move_line_end_1 - Line ID does not exist")
    else:
        # Move the tkinter selection circle for the 'start' of the line
        lines[str(line_id)]["canvas"].move(lines[str(line_id)]["end1"], xdiff, ydiff)
        # Update the line coordinates to reflect the changed 'start' position
        end1x, end1y, end2x, end2y = lines[str(line_id)]["canvas"].coords(lines[str(line_id)]["line"])
        x1, y1, x2, y2 = lines[str(line_id)]["canvas"].coords(lines[str(line_id)]["end1"])
        lines[str(line_id)]["canvas"].coords(lines[str(line_id)]["line"], (x1+x2)/2, (y1+y2)/2, end2x, end2y)
        # Update the position of the line end stops to reflect the new line geometry
        x1, y1, x2, y2 = lines[str(line_id)]["canvas"].coords(lines[str(line_id)]["line"])
        dx, dy = get_endstop_offsets(x1, y1, x2, y2)
        lines[str(line_id)]["canvas"].coords(lines[str(line_id)]["stop1"], x1+dx, y1+dy, x1-dx, y1-dy)
        lines[str(line_id)]["canvas"].coords(lines[str(line_id)]["stop2"], x2+dx, y2+dy, x2-dx, y2-dy)
    return()

def move_line_end_2(line_id:int, xdiff:int,ydiff:int):
    if not isinstance(line_id, int):
        logging.error("Line "+str(line_id)+": move_line_end_2 - Line ID must be an int")
    elif not line_exists(line_id):
        logging.error("Line "+str(line_id)+": move_line_end_2 - Line ID does not exist")
    else:
        # Move the tkinter selection circle for the 'end' of the line
        lines[str(line_id)]["canvas"].move(lines[str(line_id)]["end2"], xdiff, ydiff)
        # Update the line coordinates to reflect the changed 'end' position
        end1x, end1y, end2x, end2y = lines[str(line_id)]["canvas"].coords(lines[str(line_id)]["line"])
        x1, y1, x2, y2 = lines[str(line_id)]["canvas"].coords(lines[str(line_id)]["end2"])
        lines[str(line_id)]["canvas"].coords(lines[str(line_id)]["line"], end1x, end1y, (x1+x2)/2, (y1+y2)/2)
        # Update the position of the line end stops to reflect the new line geometry
        x1, y1, x2, y2 = lines[str(line_id)]["canvas"].coords(lines[str(line_id)]["line"])
        dx, dy = get_endstop_offsets(x1, y1, x2, y2)
        lines[str(line_id)]["canvas"].coords(lines[str(line_id)]["stop1"], x1+dx, y1+dy, x1-dx, y1-dy)
        lines[str(line_id)]["canvas"].coords(lines[str(line_id)]["stop2"], x2+dx, y2+dy, x2-dx, y2-dy)
    return()

# -------------------------------------------------------------------------
# Public API function to change the colour of a line
# -------------------------------------------------------------------------

def set_line_colour(line_id:int, colour:str):
    if not isinstance(line_id, int):
        logging.error("Line "+str(line_id)+": set_line_colour - Line ID must be an int")
    elif not line_exists(line_id):
        logging.error("Line "+str(line_id)+": set_line_colour - Line ID does not exist")
    else:
        lines[str(line_id)]["canvas"].itemconfig(lines[str(line_id)]["line"],fill=colour)
    return()

# -------------------------------------------------------------------------
# Public API function to set the colour of a line back to default
# -------------------------------------------------------------------------

def reset_line_colour(line_id:int):
    if not isinstance(line_id, int):
        logging.error("Line "+str(line_id)+": reset_line_colour - Line ID must be an int")
    elif not line_exists(line_id):
        logging.error("Line "+str(line_id)+": reset_line_colour - Line ID does not exist")
    else:
        lines[str(line_id)]["canvas"].itemconfig(lines[str(line_id)]["line"],fill=lines[str(line_id)]["colour"])
    return()

#---------------------------------------------------------------------------------------------
# API function to delete a line library object (including all the drawing objects)
# This is used by the schematic editor for updating the line config where we delete the existing
# line object with all its data and then recreate it (with the same ID) in its new configuration.
#---------------------------------------------------------------------------------------------

def delete_line(line_id:int):
    global lines
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(line_id, int):
        logging.error("Line "+str(line_id)+": delete_line - Line ID must be an int")    
    elif not line_exists(line_id):
        logging.error("Line "+str(line_id)+": delete_line - Line ID does not exist")
    else:
        logging.debug("Line "+str(line_id)+": Deleting library object from the schematic")    
        # Delete all the tkinter drawing objects associated with the line
        lines[str(line_id)]["canvas"].delete(lines[str(line_id)]["tags"])
        # Delete the line entry from the dictionary of lines
        del lines[str(line_id)]
    return()

###############################################################################################

