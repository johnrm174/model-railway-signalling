#---------------------------------------------------------------------------------------------------
# This module is used for creating and managing track sensor library objects on the canvas
#---------------------------------------------------------------------------------------------------
#
# External API - classes and functions (used by the Schematic Editor):
# 
#   track_sensor_callback_type (tells the calling program what has triggered the callback):
#      track_sensor_callback_type.sensor_triggered (the track sensor has been triggered)
# 
#   create_track_sensor - Creates a track sensior and returns a "tag" for all tkinter canvas drawing objects 
#                         This allows the editor to move the track sensor object on the schematic as required
#     Mandatory Parameters:
#        Canvas - The Tkinter Drawing canvas on which the track sensor is to be displayed
#        sensor_id:int - The unique ID for the track sensor
#        x:int, y:int - Position of the point on the canvas (in pixels)
#        callback - the function to call on track sensor triggered events
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

import enum
import logging
import tkinter as Tk

from . import common

#---------------------------------------------------------------------------------------------------
# Public API classes (to be used by external functions)
#---------------------------------------------------------------------------------------------------

class track_sensor_callback_type(enum.Enum):
    sensor_triggered = 61   # The sensor has been triggered (by the user or an GPIO sensor)

#---------------------------------------------------------------------------------------------------
# Track Sensors are maintained in a global dictionary (with a key of 'sensor_id')
# Each dictionary entry (representing a track sensor) is a dictionary of key-value pairs:
#   'canvas' - The tkinter canvas (that the drawing objects are created on) 
#   'callback' - The callback function to make on track sensor triggered events
#   'button' - A reference to the Tkinter Button object (to simulate 'sensor triggered' events)
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
    # Update all existing library objects (according to the current mode)
    for track_sensor_id in track_sensors:
        track_sensor = track_sensors[track_sensor_id]
        if editing_enabled:
            track_sensor["canvas"].itemconfig(track_sensor["circle"], width=1)
            track_sensor["canvas"].itemconfig(track_sensor["label"], state="normal")
        else:
            track_sensor["canvas"].itemconfig(track_sensor["circle"], width=0)
            track_sensor["canvas"].itemconfig(track_sensor["label"], state="hidden")
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
        callback(sensor_id, track_sensor_callback_type.sensor_triggered)
    return ()

def reset_sensor_button (sensor_id:int):
    if track_sensor_exists(sensor_id): track_sensors[str(sensor_id)]["button"].config(bg=common.bgraised)

#---------------------------------------------------------------------------------------------------
# API Function to create a Track Sensor library object on the schematic
#---------------------------------------------------------------------------------------------------

def create_track_sensor(canvas, sensor_id:int, x:int, y:int, callback):
    global track_sensors
    # Set a unique 'tag' to reference the tkinter drawing objects
    canvas_tag = "sensor"+str(sensor_id)
    if not isinstance(sensor_id, int) or sensor_id < 1 or sensor_id > 99:
        logging.error("Track Sensor "+str(sensor_id)+": create_track_sensor - Sensor ID must be an int (1-99)")
    elif track_sensor_exists(sensor_id):
        logging.error("Track Sensor "+str(sensor_id)+": create_track_sensor - Sensor ID already exists")
    else:
        logging.debug("Track Sensor "+str(sensor_id)+": Creating library object on the schematic")
        # Create the new drawing objects (tagged with the canvas_tag) - the oval is to give us
        # a reasonable selection area when we subsequently get the bbox of the tagged objects.
        # The Sensor identifier is only displayed in Edit mode (to aid configuration) - Note
        # that the label is offset to take into account the default font size in 'common'
        sensor_button = Tk.Button(canvas, text="O", padx=1, pady=1, font=('Courier',2,"normal"))
        sensor_button.config(command=lambda:track_sensor_triggered(sensor_id))
        canvas.create_window(x, y, window=sensor_button, tags=canvas_tag)
        selection_circle = canvas.create_oval(x-20, y-20, x+20, y+20, outline="grey60", tags=canvas_tag, width=0)
        sensor_label = canvas.create_text(x, y+9+(common.fontsize/2), text=format(sensor_id,'02d'), tags=canvas_tag,
                                          state="hidden", font=('Courier',common.fontsize,"normal"))
        # If we are in edit mode then the selection circle is visible
        if editing_enabled:
            canvas.itemconfig(selection_circle, width=1)
            canvas.itemconfig(sensor_label, state="normal")
        # Store the details of the Track Sensor Object in the dictionary of Track Sensors
        track_sensors[str(sensor_id)] = {}
        track_sensors[str(sensor_id)]['canvas'] = canvas
        track_sensors[str(sensor_id)]['button'] = sensor_button
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