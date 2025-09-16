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
#       line_width:str - Width of the line - default = 3
#       line_style:[int,int,] - Dash style for the line (default [] = solid)
#
#   update_line_styles - updates the styles of a line object
#     Mandatory Parameters:
#       point_id:int - The ID for the point
#     Optional Parameters:
#       colour:str - Any tkinter colour can be specified as a string - default = "Black"
#       line_width:str - Width of the line - default = 3
#       line_style:[int,int,] - Dash style for the line (default [] = solid)
#
#   line_exists(line_id:int) - returns true if the Button object 'exists' on the schematic
#
#   delete_line(line_id:int) - Delete the library object from the schematic
#
#   set_line_colour(line_id:int, colour:str) - change the colour of a line
#
#   reset_line_colour(line_id:int) - reset the colour of a line back to default
#
#   set_line_colour_override(line_id:int, colour:str) - Override the line colour
#
#   reset_line_colour_override(line_id:int) - Reset the line colour override
#
#   move_line_end_1(line_id:int, xdiff:int, ydiff:int) - Move the line end by the specified deltas
#
#   move_line_end_2(line_id:int, xdiff:int, ydiff:int) - Move the line end by the specified deltas
#
#   toggle_line_ids() - toggles the display of line IDs on/of (in Edit Mode)
#   bring_line_ids_to_front() - brings line IDs to the front (in Edit Mode)
#
# External API - classes and functions (used by the other library modules):
#
#   configure_edit_mode(edit_mode:bool) - True for Edit Mode, False for Run Mode
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
# Library function to set/clear Edit Mode (called by the editor on mode change)
#---------------------------------------------------------------------------------------------

editing_enabled = False

def configure_edit_mode(edit_mode:bool):
    global editing_enabled
    # Maintain a global flag (for creating new library objects)
    editing_enabled = edit_mode
    if edit_mode and line_ids_displayed: show_line_ids()
    else: hide_line_ids()
    return()

#---------------------------------------------------------------------------------------------
# Library function to show/hide line IDs in edit mode
#---------------------------------------------------------------------------------------------

line_ids_displayed = False

def show_line_ids():
    for line_id in lines:
        lines[str(line_id)]["canvas"].itemconfig(lines[str(line_id)]["label1"], state="normal")
        lines[str(line_id)]["canvas"].itemconfig(lines[str(line_id)]["label2"], state="normal")
    bring_line_ids_to_front()
    return()

def hide_line_ids():
    for line_id in lines:
        lines[str(line_id)]["canvas"].itemconfig(lines[str(line_id)]["label1"], state="hidden")
        lines[str(line_id)]["canvas"].itemconfig(lines[str(line_id)]["label2"], state="hidden")
    return()

def toggle_line_ids():
    global line_ids_displayed
    if not line_ids_displayed:
        line_ids_displayed = True
        show_line_ids()
    else:
        line_ids_displayed = False
        hide_line_ids()
    return()

def bring_line_ids_to_front():
    for line_id in lines:
        lines[str(line_id)]["canvas"].tag_raise(lines[str(line_id)]["label2"])
        lines[str(line_id)]["canvas"].tag_raise(lines[str(line_id)]["label1"])
    return()

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

def create_line (canvas, line_id:int, x1:int, y1:int, x2:int, y2:int, colour:str="black", line_style:list=[],
                  arrow_type:list=[0,0,0], arrow_ends:int=0, selected:bool=False, line_width:int=3):
    global lines
    # Set a unique 'tag' to reference the tkinter drawing objects
    canvas_tag = "line"+str(line_id)
    # Create an aditional tag for the line "selection" indication
    selected_tag = "line"+str(line_id)+"selected"
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(line_id, int) or line_id < 1:
        logging.error("Line "+str(line_id)+": create_line - Line ID must be a positive integer")
    elif line_exists(line_id):
        logging.error("Line "+str(line_id)+": create_line - Line ID already exists")
    else:
        logging.debug("Line "+str(line_id)+": Creating Line on the Canvas")
        # Draw the line (with arrow heads if these are selected). An arrow_type configuration
        # of [1,1,1] is used to select 'end stops' over 'arrows'. Note that we store this
        # configuration as a list rather than the tuple needed by the tkinter create_line
        # function so it is serialisable to json for save and load.
        if arrow_type != [0,0,0] and arrow_type != [1,1,1] and arrow_ends == 1:
            line_object = canvas.create_line(x1, y1, x2, y2, arrow=Tk.FIRST, arrowshape=tuple(arrow_type), tags=canvas_tag)
        elif arrow_type != [0,0,0] and arrow_type != [1,1,1] and arrow_ends == 2:
            line_object = canvas.create_line(x1, y1, x2, y2, arrow=Tk.LAST, arrowshape=tuple(arrow_type), tags=canvas_tag)
        elif arrow_type != [0,0,0] and arrow_type != [1,1,1] and arrow_ends == 3:
            line_object = canvas.create_line(x1, y1, x2, y2, arrow=Tk.BOTH, arrowshape=tuple(arrow_type), tags=canvas_tag)
        else:
            line_object = canvas.create_line(x1, y1, x2, y2, tags=canvas_tag)
        # Draw the line-end selection circles if we are in Edit Mode and the 'selected' flag is set
        # This is the case of the line being re-created (in its new configuration) after the config
        # has been changed where we want to leave the line as selected
        if selected and editing_enabled: state="normal"
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
        stop1_object = canvas.create_line(x1+dx, y1+dy, x1-dx, y1-dy, tags=canvas_tag, state=stop1)
        stop2_object = canvas.create_line(x2+dx, y2+dy, x2-dx, y2-dy, tags=canvas_tag, state=stop2)
        # Apply the line styles
        canvas.itemconfig(line_object, fill=colour, width=line_width, dash=tuple(line_style))
        canvas.itemconfig(stop1_object, fill=colour, width=line_width, dash=tuple(line_style))
        canvas.itemconfig(stop2_object, fill=colour, width=line_width, dash=tuple(line_style))
        # Create the line ID labels
        label1_object = canvas.create_text(x1+(x2-x1)/2, y1+(y2-y1)/2, text=str(line_id), font=("Courier", 9, "bold"),
                                        fill="white", tags=canvas_tag)
        bbox = canvas.bbox(label1_object)
        label2_object = canvas.create_rectangle(bbox[0]-4, bbox[1]-3, bbox[2]+4, bbox[3]+1,
                                        tags=canvas_tag, fill="purple3", width=0)
        if not editing_enabled or not line_ids_displayed:
            canvas.itemconfig(label1_object, state="hidden")
            canvas.itemconfig(label2_object, state="hidden")
        # Compile a dictionary of everything we need to track
        lines[str(line_id)] = {}
        lines[str(line_id)]["canvas"] = canvas                  # Tkinter canvas object
        lines[str(line_id)]["colouroverride"] = False           # Whether the colour is overridden or not
        lines[str(line_id)]["defaultcolour"] = colour           # Default colour for the line
        lines[str(line_id)]["currentcolour"] = colour           # Current Colour for the line
        lines[str(line_id)]["line"] = line_object               # Reference to the Tkinter drawing object
        lines[str(line_id)]["end1"] = end1_object               # Reference to the Tkinter drawing object
        lines[str(line_id)]["end2"] = end2_object               # Reference to the Tkinter drawing object
        lines[str(line_id)]["stop1"] = stop1_object             # Reference to the Tkinter drawing object
        lines[str(line_id)]["stop2"] = stop2_object             # Reference to the Tkinter drawing object
        lines[str(line_id)]["label1"] = label1_object           # Reference to the Tkinter drawing object
        lines[str(line_id)]["label2"] = label2_object           # Reference to the Tkinter drawing object
        lines[str(line_id)]["tags"] = canvas_tag                # Canvas Tag for ALL drawing objects
    # Return the canvas tag references
    return(canvas_tag, selected_tag)

#---------------------------------------------------------------------------------------------
# Public API function to Update the Line Styles
#---------------------------------------------------------------------------------------------

def update_line_styles(line_id:int, colour:str="black", line_width:int=3, line_style:list=[]):
    global lines
    # Validate the parameters we have been given as this is a library API function
    if not isinstance(line_id, int) :
        logging.error("Line "+str(line_id)+": update_line_styles - Line ID must be an int")
    elif not line_exists(line_id):
        logging.error("Line "+str(line_id)+": update_line_styles - Line ID does not exist")
    else:
        logging.debug("Line "+str(line_id)+": Updating Line Styles")
        lines[str(line_id)]["canvas"].itemconfig(lines[str(line_id)]["line"], width=line_width, dash=tuple(line_style))
        lines[str(line_id)]["canvas"].itemconfig(lines[str(line_id)]["stop1"], width=line_width, dash=tuple(line_style))
        lines[str(line_id)]["canvas"].itemconfig(lines[str(line_id)]["stop2"], width=line_width, dash=tuple(line_style))
        lines[str(line_id)]["defaultcolour"] = colour
        lines[str(line_id)]["currentcolour"] = colour
        reset_line_colour(line_id)
    return()

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
        # Update the position of the line id label
        lines[str(line_id)]["canvas"].move(lines[str(line_id)]["label1"], xdiff/2, ydiff/2)
        lines[str(line_id)]["canvas"].move(lines[str(line_id)]["label2"], xdiff/2, ydiff/2)

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
        # Update the position of the line id label
        lines[str(line_id)]["canvas"].move(lines[str(line_id)]["label1"], xdiff/2, ydiff/2)
        lines[str(line_id)]["canvas"].move(lines[str(line_id)]["label2"], xdiff/2, ydiff/2)
    return()

#--------------------------------------------------------------------------
# Public API function to change the colour of a line (for route highlighting).
# Note that this change will only be effected immediately if the line colour is not
# overridden. Otherwise the change will be applied when the colour override is reset.
#--------------------------------------------------------------------------

def set_line_colour(line_id:int, colour:str):
    if not isinstance(line_id, int):
        logging.error("Line "+str(line_id)+": set_line_colour - Line ID must be an int")
    elif not line_exists(line_id):
        logging.error("Line "+str(line_id)+": set_line_colour - Line ID does not exist")
    else:
        if not lines[str(line_id)]["colouroverride"]:
            lines[str(line_id)]["canvas"].itemconfig(lines[str(line_id)]["line"],fill=colour)
            lines[str(line_id)]["canvas"].itemconfig(lines[str(line_id)]["stop1"],fill=colour)
            lines[str(line_id)]["canvas"].itemconfig(lines[str(line_id)]["stop2"],fill=colour)
        lines[str(line_id)]["currentcolour"] = colour
    return()

#--------------------------------------------------------------------------
# Public API function to reset the colour of a line back to its default
# (for when a route is un-highlighted). Note that this change will only be
# effected immediately if the line colour is not overridden. Otherwise the
# change will be applied when the colour override is reset.
#--------------------------------------------------------------------------

def reset_line_colour(line_id:int):
    if not isinstance(line_id, int):
        logging.error("Line "+str(line_id)+": reset_line_colour - Line ID must be an int")
    elif not line_exists(line_id):
        logging.error("Line "+str(line_id)+": reset_line_colour - Line ID does not exist")
    else:
        if not lines[str(line_id)]["colouroverride"]:
            default_colour = lines[str(line_id)]["defaultcolour"]
            lines[str(line_id)]["canvas"].itemconfig(lines[str(line_id)]["line"],fill=default_colour)
            lines[str(line_id)]["canvas"].itemconfig(lines[str(line_id)]["stop1"],fill=default_colour)
            lines[str(line_id)]["canvas"].itemconfig(lines[str(line_id)]["stop2"],fill=default_colour)
        lines[str(line_id)]["currentcolour"] = lines[str(line_id)]["defaultcolour"]
    return()

#--------------------------------------------------------------------------
# Public API function to override the colour of a line. This overrides any
# current highlighting (by 'set_line_colour' and 'reset_line_colour' functions)
#--------------------------------------------------------------------------

def set_line_colour_override(line_id:int, colour:str):
    if not isinstance(line_id, int):
        logging.error("Line "+str(line_id)+": set_line_colour_override - Line ID must be an int")
    elif not line_exists(line_id):
        logging.error("Line "+str(line_id)+": set_line_colour_override - Line ID does not exist")
    else:
        lines[str(line_id)]["colouroverride"] = True
        lines[str(line_id)]["canvas"].itemconfig(lines[str(line_id)]["line"],fill=colour)
        lines[str(line_id)]["canvas"].itemconfig(lines[str(line_id)]["stop1"],fill=colour)
        lines[str(line_id)]["canvas"].itemconfig(lines[str(line_id)]["stop2"],fill=colour)
    return()

#--------------------------------------------------------------------------
# Public API function to reset the colour of a line to its 'normal' colour
# (as configured by the 'set_line_colour' and 'reset_line_colour' functions).
#--------------------------------------------------------------------------

def reset_line_colour_override(line_id:int):
    if not isinstance(line_id, int):
        logging.error("Line "+str(line_id)+": reset_line_colour_override - Line ID must be an int")
    elif not line_exists(line_id):
        logging.error("Line "+str(line_id)+": reset_line_colour_override - Line ID does not exist")
    else:
        lines[str(line_id)]["colouroverride"] = False
        current_colour = lines[str(line_id)]["currentcolour"]
        lines[str(line_id)]["canvas"].itemconfig(lines[str(line_id)]["line"],fill=current_colour)
        lines[str(line_id)]["canvas"].itemconfig(lines[str(line_id)]["stop1"],fill=current_colour)
        lines[str(line_id)]["canvas"].itemconfig(lines[str(line_id)]["stop2"],fill=current_colour)
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

