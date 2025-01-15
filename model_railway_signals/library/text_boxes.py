#---------------------------------------------------------------------------------------------------
# This module is used for creating and managing text box library objects on the canvas
#---------------------------------------------------------------------------------------------------
#
# External API - classes and functions (used by the Schematic Editor):
# 
#   create_text_box - Creates a text box and returns a "tag" for the tkinter canvas drawing objects
#                     This allows the editor to move the text box object on the schematic as required
#     Mandatory Parameters:
#        Canvas - The Tkinter Drawing canvas on which the text box is to be displayed
#        textbox_id:int - The unique ID for the text box
#        x:int, y:int - Position of the text box on the canvas (in pixels)
#        text:str - The text to display
#     Optional Parameters:
#        colour:str - Text colour - default="black"
#        background:str - Background colour - default="grey85"
#        justify: either TK.LEFT, TK.CENTRE, TK.RIGHT - default=TK.CENTER
#        borderwidth:int - the width of the border to display - default=0 (no border)
#        font:(str,int,str) - the font to apply - default=("Courier",8,"normal")
#        hidden:bool - Whether the text box should be 'hidden' in Run Mode - default=False
#
#   update_text_box_styles - Update the styles of an existing library object
#     Mandatory Parameters:
#        textbox_id:int - The unique ID for the text box
#     Optional Parameters:
#        colour:str - Text colour - default="black"
#        background:str - Background colour - default="grey85"
#        justify: either TK.LEFT, TK.CENTRE, TK.RIGHT - default=TK.CENTER
#        borderwidth:int - the width of the border to display - default=0 (no border)
#        font:(str,int,str) - the font to apply - default=("Courier",8,"normal")
#
#    text_box_exists(textbox_id:int) - returns true if the if a text box object 'exists'
#
#    delete_text_box(textbox_id:int) - To delete the specified text box from the schematic
#
# Classes and functions used by the other library modules:
#
#   configure_edit_mode(edit_mode:bool) - True for Edit Mode, False for Run Mode
#
#---------------------------------------------------------------------------------------------------

import logging
import tkinter as Tk

#---------------------------------------------------------------------------------------------------
# Text Boxes are maintained in a global dictionary (with a key of 'textbox_id')
# Each dictionary entry (representing a text box) is a dictionary of key-value pairs:
#   'canvas' - The tkinter canvas (that the drawing objects are created on) 
#   'hiddden' - Whether the Text Box should be 'hidden' in Run Mode or not
#   'textwidget' - Reference to the Tkinter drawing object
#   'rectangle' -  Reference to the Tkinter drawing object
#   'borderwidth' - Borderwidth for the rectangle (so this can be hidden/displayed)
#   'background' - Background colour for the rectangle (so this can be hidden/displayed)
#   'tags' - The tags applied to the text box objects on the canvas
#---------------------------------------------------------------------------------------------------

text_boxes = {}

#------------------------------------------------------------------------------------
# API function to set/clear Edit Mode (called by the editor on mode change)
# Text Box objects are 'hidden' in Run Mode if this is configured at creation
#------------------------------------------------------------------------------------

editing_enabled = False

def configure_edit_mode(edit_mode:bool):
    global editing_enabled
    # Maintain a global flag (for creating new library objects)
    editing_enabled = edit_mode
    for text_box_id in text_boxes:
        text_box = text_boxes[text_box_id]
        if editing_enabled:
            # In Edit Mode - Always display all drawing objects as configured
            text_box["canvas"].itemconfig(text_box['textwidget'], state="normal")
            text_box["canvas"].itemconfig(text_box["rectangle"], width=text_box["borderwidth"], fill=text_box["background"])
        elif text_box["hidden"]:
            # In Run Mode - if the object is configured as 'hidden' then we hide the text object
            # but set the rectangle object to transparent (fill="") with a border width of zero
            text_box["canvas"].itemconfig(text_box['textwidget'], state="hidden")
            text_box["canvas"].itemconfig(text_box["rectangle"], width=0, fill="")
    return()

#---------------------------------------------------------------------------------------------------
# API Function to check if a Text Box library object exists (in the dictionary of Text Boxes)
#---------------------------------------------------------------------------------------------------

def text_box_exists(textbox_id:int):
    if not isinstance(textbox_id, int):
        logging.error("Text Box "+str(textbox_id)+": textbox_exists - textbox_id ID must be an int")
        textbox_exists = False
    else:
        textbox_exists = str(textbox_id) in text_boxes.keys() 
    return(textbox_exists)

#---------------------------------------------------------------------------------------------------
# API Function to create a Text Box library object on the schematic
#---------------------------------------------------------------------------------------------------

def create_text_box(canvas, textbox_id:int, x:int, y:int, text:str, colour:str="black",
                    background:str="grey85",  justify=Tk.CENTER, borderwidth:int=0,
                    font=("Courier",8,"normal"), hidden:bool=False):
    global text_boxes
    # Set a unique 'tag' to reference the tkinter drawing objects
    canvas_tag = 'textwidget'+str(textbox_id)
    if not isinstance(textbox_id, int) or textbox_id < 1:
        logging.error("Text Box "+str(textbox_id)+": create_text_box - Textbox ID must be a positive integer")
    elif text_box_exists(textbox_id):
        logging.error("Text Box "+str(textbox_id)+": create_text_box - Textbox ID already exists")
    else:
        logging.debug("Text Box "+str(textbox_id)+": Creating library object on the schematic")
        # Create the new drawing objects (tagged with the canvas_tag) - These are initially created
        # assuming we are in Edit Mode (Objects always visible) and hidden later if required.
        text_box = canvas.create_text(x, y, fill=colour, text=text, tags=canvas_tag,
                                      justify=justify, font=font, state='normal')
        # Find the boundary box and create the rectangle for the background
        bbox = canvas.bbox(text_box)
        rectangle = canvas.create_rectangle(bbox[0]-3, bbox[1]-3, bbox[2]+3, bbox[3]+2,
                    width=borderwidth, tags=canvas_tag, fill=background, outline=colour, state='normal')
        # Raise the text item to be in front of the rectangle item
        canvas.tag_raise(text_box, rectangle)
        # Hide the drawing objects if we are in Run Mode and 'hidden'. Note we can't just make the
        # rectangle 'hidden' as the canvas.bbox function (used by the editor to get the selection area)
        # would just return zero values when subsequently queried (after the return from this function)
        # and so the object would be unselectable when the user toggles back to edit mode. We therefore
        # set the rectangle borderwidth to zero and make it transparent (fill="")
        if not editing_enabled and hidden:
            canvas.itemconfig(text_box, state="hidden")
            canvas.itemconfig(rectangle, fill="", width=0)
        # Store the details of the Text Box Object in the dictionary of Text boxes
        text_boxes[str(textbox_id)] = {}
        text_boxes[str(textbox_id)]['canvas'] = canvas
        text_boxes[str(textbox_id)]['textwidget'] = text_box
        text_boxes[str(textbox_id)]['rectangle'] = rectangle
        text_boxes[str(textbox_id)]['borderwidth'] = borderwidth
        text_boxes[str(textbox_id)]['background'] = background
        text_boxes[str(textbox_id)]['hidden'] = hidden
        text_boxes[str(textbox_id)]['tags'] = canvas_tag
        # Return the canvas_tag for the tkinter drawing objects
    return(canvas_tag)

#---------------------------------------------------------------------------------------------------
# API Function to create a Text Box library object on the schematic
#---------------------------------------------------------------------------------------------------

def update_text_box_styles(textbox_id:int, colour:str="black", background:str="grey85",
            justify=Tk.CENTER, borderwidth:int=0, font=("Courier",8,"normal"), hidden:bool=False):
    global text_boxes
    if not isinstance(textbox_id, int) :
        logging.error("Text Box "+str(textbox_id)+": create_text_box - Textbox ID must be a an int")
    elif not text_box_exists(textbox_id):
        logging.error("Text Box "+str(textbox_id)+": update_text_box_styles - Textbox ID does not exist")
    else:
        logging.debug("Text Box "+str(textbox_id)+": Updating Textbox Styles")
        # Update the Textbox Styles. This is relatively complex operation as we first
        # need to ensure the text isn't "hidden" otherwise we will not be able to use the
        # 'bbox' method to get the new boundary coordinates (after we have updated the font).
        textbox = text_boxes[str(textbox_id)]
        if not editing_enabled and textbox["hidden"]:
            textbox["canvas"].itemconfig(textbox['textwidget'], state='normal')
        textbox["canvas"].itemconfigure(textbox["textwidget"], font=font)
        textbox["canvas"].itemconfigure(textbox["textwidget"], fill=colour)
        bbox = textbox["canvas"].bbox(textbox["textwidget"])
        # Now we have the boundary coordinates we can re-hide the text (if hidden in run mode)
        if not editing_enabled and textbox["hidden"]:
            textbox["canvas"].itemconfigure(textbox["textwidget"], state='hidden')
        # The background rectangle can now be updated as required
        textbox["canvas"].coords(textbox["rectangle"], bbox[0]-3, bbox[1]-3, bbox[2]+3, bbox[3]+2)
        if editing_enabled or not textbox["hidden"]:
            textbox["canvas"].itemconfig(textbox["rectangle"], fill=background)
            textbox["canvas"].itemconfig(textbox["rectangle"], width=borderwidth)
        # Store the parameters we need to track
        text_boxes[str(textbox_id)]['borderwidth'] = borderwidth
        text_boxes[str(textbox_id)]['background'] = background
    return()

#---------------------------------------------------------------------------------------------------
# Function to delete a Text Box library object from the schematic
#---------------------------------------------------------------------------------------------------

def delete_text_box(textbox_id:int):
    global text_boxes
    if not isinstance(textbox_id, int):
        logging.error("Text Box "+str(textbox_id)+": delete_text_box - Textbox ID must be an int")
    elif not text_box_exists(textbox_id):
        logging.error("Text Box "+str(textbox_id)+": delete_text_box - Textbox ID does not exist")
    else:
        logging.debug("Text Box "+str(textbox_id)+": Deleting Textbox object from the schematic")
        # Delete all tkinter drawing objects
        text_boxes[str(textbox_id)]['canvas'].delete(text_boxes[str(textbox_id)]["tags"])
        # Delete the track sensor entry from the dictionary of track sensors
        del text_boxes[str(textbox_id)]
    return()

#####################################################################################################