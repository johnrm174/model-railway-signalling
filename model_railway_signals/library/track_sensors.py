#---------------------------------------------------------------------------------------------------
# This module is used for creating and managing track sensor library objects on the canvas
#---------------------------------------------------------------------------------------------------
#
# External API - classes and functions (used by the Schematic Editor):
# 
#   create_track_sensor - Creates a track sensior and returns a "tag" for all tkinter canvas drawing objects 
#                         This allows the editor to move the track sensor object on the schematic as required
#     Mandatory Parameters:
#        Canvas - The Tkinter Drawing canvas on which the track sensor is to be displayed
#        sensor_id:int - The unique ID for the track sensor
#        x:int, y:int - Position of the track sensor on the canvas (in pixels)
#        callback - the function to call on track sensor triggered events (returns item_id)
#     Optional Parameters:
#        hidden:bool - Whether the Track Sensor should be 'hidden' in Run Mode - default = False
#
#    track_sensor_exists(sensor_id:int) - returns true if the if a track sensor object 'exists'
#
#    delete_track_sensor(sensor_id:int) - To delete the specified track sensor from the schematic
#
# Classes and functions used by the other library modules:
#
#   track_sensor_triggered(sensor_id:int, callback_type=None) - Called on gpio_sensor trigger
#         events if the gpio_sensor has been configured to generate a "track sensor passed" event
#
#   configure_edit_mode(edit_mode:bool) - True for Edit Mode, False for Run Mode
#
#---------------------------------------------------------------------------------------------------

import logging
import tkinter as Tk

from . import common

#---------------------------------------------------------------------------------------------------
# Track Sensors are maintained in a global dictionary (with a key of 'sensor_id')
# Each dictionary entry (representing a track sensor) is a dictionary of key-value pairs:
#   'canvas' - The tkinter canvas (that the drawing objects are created on) 
#   'callback' - The callback function to make on track sensor triggered events
#   'hiddden' - Whether the Track Sensor should be 'hidden' in Run Mode or not
#   'button' - A reference to the Tkinter Button object (to simulate 'sensor triggered' events)
#   'buttonwindow' - A reference to the Tkinter Button window (so this can be hidden/displayed)
#   'tags' - The tags applied to all canvas drawing objects for the Track Sensor instance
#   'circle' - The reference to the Tkinter circle used for "selection" in edit mode
#   'label' - The reference to the Tkinter label which is only displayed in edit mode
#---------------------------------------------------------------------------------------------------

track_sensors = {}

#------------------------------------------------------------------------------------
# API function to set/clear Edit Mode (called by the editor on mode change)
# The appearance of Track Sensor library objects will change in Edit Mode
#------------------------------------------------------------------------------------

editing_enabled = False

def configure_edit_mode(edit_mode:bool):
    global editing_enabled
    # Maintain a global flag (for creating new library objects)
    editing_enabled = edit_mode
    # Update all canvas objects depending on the mode and whether the sensor should be 'hidden' (in Run Mode)
    # In Edit mode - all drawing objects (button, selection circle and Item ID text) are visible
    # In Run Mode, only the button is visible (unless this needs to be 'hidden' in Run Mode
    for track_sensor_id in track_sensors:
        track_sensor = track_sensors[track_sensor_id]
        if editing_enabled:
            track_sensor["canvas"].itemconfig(track_sensor["circle"], width=1)
            track_sensor["canvas"].itemconfig(track_sensor["label"], state="normal")
            track_sensor["canvas"].itemconfig(track_sensor["buttonwindow"], state="normal")
        else:
            if track_sensor["hidden"]:
                track_sensor["canvas"].itemconfig(track_sensor["buttonwindow"], state="hidden")
            track_sensor["canvas"].itemconfig(track_sensor["label"], state="hidden")
            track_sensor["canvas"].itemconfig(track_sensor["circle"], width=0)
    return()

#---------------------------------------------------------------------------------------------------
# API Function to check if a Track Sensor library object exists (in the dictionary of Track Sensors)
#---------------------------------------------------------------------------------------------------

def track_sensor_exists(sensor_id:int):
    if not isinstance(sensor_id, int):
        logging.error("Track Sensor "+str(sensor_id)+": track_sensor_exists - Sensor ID must be an int")
        sensor_exists = False
    else:
        sensor_exists = str(sensor_id) in track_sensors.keys() 
    return (sensor_exists)

#---------------------------------------------------------------------------------------------------
# API function called from the gpio_sensors module on GPIO trigger events (if a gpio sensor has 
# been configured to raise "track sensor passed" events). Also used internally to track sensor
# button press events (to simulate the "track sensor passed" event).
#---------------------------------------------------------------------------------------------------

def track_sensor_triggered (sensor_id:int, callback_type=None):
    if not isinstance(sensor_id, int):
        logging.error("Track Sensor "+str(sensor_id)+": track_sensor_triggered - Sensor ID must be an int")
    elif not track_sensor_exists(sensor_id):
        logging.error("Track Sensor "+str(sensor_id)+": track_sensor_triggered - Sensor ID does not exist")
    else:
        logging.info("Track Sensor "+str(sensor_id)+": Track Sensor Passed Event ****************************************")
        # Pulse the button to provide a visual indication (but not if a shutdown has been initiated)
        if not common.shutdown_initiated:
            track_sensors[str(sensor_id)]["button"].config(bg="red")
            common.root_window.after(1000,lambda:reset_sensor_button(sensor_id))
        # Make the external callback specified for the track sensor
        callback = track_sensors[str(sensor_id)]["callback"]
        callback(sensor_id)
    return ()

def reset_sensor_button (sensor_id:int):
    if track_sensor_exists(sensor_id): track_sensors[str(sensor_id)]["button"].config(bg="grey85")

#---------------------------------------------------------------------------------------------------
# API Function to create a Track Sensor library object on the schematic
#---------------------------------------------------------------------------------------------------

def create_track_sensor(canvas, sensor_id:int, x:int, y:int, callback, hidden:bool=False):
    global track_sensors
    # Set a unique 'tag' to reference the tkinter drawing objects
    canvas_tag = "sensor"+str(sensor_id)
    if not isinstance(sensor_id, int) or sensor_id < 1 or sensor_id > 999:
        logging.error("Track Sensor "+str(sensor_id)+": create_track_sensor - Sensor ID must be an int (1-999)")
    elif track_sensor_exists(sensor_id):
        logging.error("Track Sensor "+str(sensor_id)+": create_track_sensor - Sensor ID already exists")
    else:
        logging.debug("Track Sensor "+str(sensor_id)+": Creating library object on the schematic")
        # Create the new drawing objects (tagged with the canvas_tag) - the Oval object and Sensor ID text are
        # only displayed in Edit mode (to aid identification and selection). These are both initially created
        # assuming we are in Run Mode (Oval has a width of zero to make it invisible and the text is hidden).
        # Similarly the button is created as visible (Changed later if in Run Mode and 'hidden' is selected)
        sensor_button = Tk.Button(canvas, text="O", padx=1, pady=1, font=('Courier',2,"normal"), highlightthickness=0)
        sensor_button.config(command=lambda:track_sensor_triggered(sensor_id))
        button_window = canvas.create_window(x, y, window=sensor_button, tags=canvas_tag)
        selection_circle = canvas.create_oval(x-20, y-20, x+20, y+20, outline="grey60", tags=canvas_tag, width=0)
        # Note that the label is offset to take into account the default font size in 'common'
        sensor_label = canvas.create_text(x, y-10, text=format(sensor_id,'02d'), tags=canvas_tag,
                                          state="hidden", font=('Courier',8,"bold"))
        # In Edit mode - all drawing objects (button, selection circle and Item ID text) are visible
        # In Run Mode, only the button is visible (unless this needs to be 'hidden' in Run Mode)
        if editing_enabled:
            canvas.itemconfig(selection_circle, width=1)
            canvas.itemconfig(sensor_label, state="normal")
        elif hidden:
            canvas.itemconfig(button_window, state='hidden')
        # Store the details of the Track Sensor Object in the dictionary of Track Sensors
        track_sensors[str(sensor_id)] = {}
        track_sensors[str(sensor_id)]['canvas'] = canvas
        track_sensors[str(sensor_id)]['button'] = sensor_button
        track_sensors[str(sensor_id)]['buttonwindow'] = button_window
        track_sensors[str(sensor_id)]['hidden'] = hidden
        track_sensors[str(sensor_id)]['callback'] = callback
        track_sensors[str(sensor_id)]['tags'] = canvas_tag
        track_sensors[str(sensor_id)]['circle'] = selection_circle
        track_sensors[str(sensor_id)]['label'] = sensor_label
        # Return the canvas_tag for the tkinter drawing objects
    return(canvas_tag)

#---------------------------------------------------------------------------------------------------
# Function to delete a Track Sensor library object from the schematic
#---------------------------------------------------------------------------------------------------

def delete_track_sensor(sensor_id:int):
    global track_sensors
    if not isinstance(sensor_id, int):
        logging.error("Track Sensor "+str(sensor_id)+": delete_track_sensor - Sensor ID must be an int")
    elif not track_sensor_exists(sensor_id):
        logging.error("Track Sensor "+str(sensor_id)+": delete_track_sensor - Sensor ID does not exist")
    else:
        logging.debug("Track Sensor "+str(sensor_id)+": Deleting library object from the schematic")
        # Delete all tkinter drawing objects
        track_sensors[str(sensor_id)]['canvas'].delete(track_sensors[str(sensor_id)]["tags"])
        track_sensors[str(sensor_id)]['button'].destroy()
        # Delete the track sensor entry from the dictionary of track sensors
        del track_sensors[str(sensor_id)]
    return()

#####################################################################################################