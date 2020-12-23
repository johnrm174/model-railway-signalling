from tkinter import *
import tkinter.font
import common

# --------------------------------------------------------------------------------
# This module is used for creating and managing switch objects (buttons)
# Two types are supported:
#   1) A simple switch - represented by a single button - toggle between on/off
#   2) A two way centre-off switch - represented by two buttons - toggle on1/off/on2  
#
# The following functions are designed to be called by external modules
#
# create_switch - Creates a switch object
#   Mandatory Parameters:
#       Canvas - The Tkinter Drawing canvas on which the switch is to be displayed
#       switch_id:int - The ID to be used for the switch 
#       x:int, y:int - Position of the point on the canvas (in pixels)
#   Optional Parameters:
#       switch_callback - The function to call whenever the switch is changed - default: null
#       label1 - The label to display on the switch button - default: empty string
#       label2 - The label to display on the second switch button - default: empty string
#       two_way - If true then the switch is two-way (i.e. second button) - default: False
#       bg_inactive - The background colour when the button is off - default 'SeaGreen3'
#       bg_active - The background colour when the button is on - default 'SeaGreen1'
#       fg_active - The text colour when the button is on - default 'Black'
#       fg_inactive - The text colour when the button is off - default 'Black'
#
# switch_active - Returns the current state of the switch (True/False)
#   Mandatory Parameters:
#       switch_id:int - The ID of the switch
#   Optional Parameters (only required for two way switches):
#       button_id:int - The Button to query the state of (1 or 2) - Default: 1
#
# set_switch - Sets the specified switch button to "on"
#   Mandatory Parameters:
#       switch_id:int - The ID of the switch
#   Optional Parameters (only required for two way switches):
#       button_id:int - The Button to set the state of (1 or 2) - Default: 1
#
# clear_switch - - Sets the specified switch button to "off"
#   Mandatory Parameters:
#       switch_id:int - The ID of the switch
#   Optional Parameters (only required for two way switches):
#       button_id:int - The Button to clear the state of (1 or 2) - Default: 1
#
# --------------------------------------------------------------------------------


# -------------------------------------------------------------------------
# Switches are to be added to a global dictionary when created
# -------------------------------------------------------------------------

# Define an empty dictionary 
switches: dict = {}

# -------------------------------------------------------------------------
# The default "External" callback for the switch buttons
# Used if this is  not specified when the switch is created
# -------------------------------------------------------------------------

def switch_null(switch_id, button_id:int=1):
    return(switch_id, button_id)

# -------------------------------------------------------------------------
# Internal Function to check if a Switch exists in the list of Switches
# Used in Most externally-called functions to validate the Switch_ID
# -------------------------------------------------------------------------

def switch_exists(switch_id):
    return (str(switch_id) in switches.keys() )

# -------------------------------------------------------------------------
# Internal function to flip the state of the Switch. This Will SET/UNSET
# the switch and initiate an external callback if one is specified
# -------------------------------------------------------------------------

def toggle_switch (switch_id:int,button_id:int, ext_callback=switch_null ):

    global switches # the dictionary of switches

    # Validate the switch exists 
    if not switch_exists(switch_id):
        print ("ERROR: toggle_switch - Switch "+str(switch_id)+" does not exist")
    else:

        switch = switches[str(switch_id)]
        if button_id == 1:
            if switch["switch1"] == True:  # Switch is on
                switch["switch1"] = False
                switch["button1"].config(relief="raised",bg=switch["bginactive"],fg=switch["fginactive"],
                                activebackground=switch["bginactive"], activeforeground=switch["fginactive"])
            else:  # Switch is off
                # Activate the Button
                switch["switch1"] = True
                switch["button1"].config(relief="sunken",bg=switch["bgactive"],fg=switch["fgactive"],
                                activebackground=switch["bgactive"], activeforeground=switch["fgactive"])
                # De-activate the other button
                switch["switch2"] = False
                switch["button2"].config(relief="raised",bg=switch["bginactive"],fg=switch["fginactive"],
                                activebackground=switch["bginactive"], activeforeground=switch["fginactive"])

        elif button_id == 2:
            if switch["switch2"] == True:  # Switch is on
                switch["switch2"] = False
                switch["button2"].config(relief="raised",bg=switch["bginactive"],fg=switch["fginactive"],
                                activebackground=switch["bginactive"], activeforeground=switch["fginactive"])

            else:  # Switch is off
                # Activate the Button
                switch["switch2"] = True
                switch["button2"].config(relief="sunken",bg=switch["bgactive"],fg=switch["fgactive"],
                                activebackground=switch["bgactive"], activeforeground=switch["fgactive"])

                # De-activate the other button
                switch["switch1"] = False
                switch["button1"].config(relief="raised",bg=switch["bginactive"],fg=switch["fginactive"],
                                activebackground=switch["bginactive"], activeforeground=switch["fginactive"])

        # update the dictionary of switches with the new state  
        switches[str(switch_id)] = switch;
        
        # Now make the external callback
        ext_callback(switch_id, button_id)

    return()

# -------------------------------------------------------------------------
# Externally called function to create a Switch (drawing objects + state)
# All attributes (that need to be tracked) are stored as a dictionary
# This is then added to a dictionary of Switches for later reference
# -------------------------------------------------------------------------

def create_switch (canvas, switch_id:int, x:int, y:int, switch_callback = switch_null,
                   label1:str="", label2:str="", two_way:bool=False,
                   bg_inactive:str="SeaGreen3",bg_active:str="SeaGreen1",
                   fg_active:str="Black",fg_inactive:str="Black"):
    
    global switches # the dictionary of switches
    # also uses fontsize, xpadding, ypadding imported from "common"

    # Verify that a switch with the same ID does not already exist
    if switch_exists(switch_id):
        print ("ERROR: create_switch - switch ID "+str(switch_id)+" already exists")
    elif switch_id < 1:
        print ("ERROR: create_switch - switch ID must be greater than zero")
    else: # we're good to go on and create the switch
        
        # set the font size for the buttons
        myfont = tkinter.font.Font(size=common.fontsize)

        # Create the button objects and their callbacks
        button1 = Button (canvas,text=label1,state="normal",
                    padx=common.xpadding,pady=common.ypadding,
                    relief="raised", font=myfont, bg=bg_inactive, fg=fg_inactive,
                    activebackground=bg_inactive, activeforeground=fg_inactive,
                    command = lambda:toggle_switch(switch_id,1,switch_callback))
        button2 = Button (canvas,text=label2,state="normal",padx=common.xpadding,pady=common.ypadding,
                    relief="raised", font=myfont, bg=bg_inactive, fg=fg_inactive,
                    activebackground=bg_inactive, activeforeground=fg_inactive,
                    command = lambda:toggle_switch(switch_id,2,switch_callback))

        #Create some drawing objects (depending on switch type)
        but1win = canvas.create_window (x,y-20,anchor=E,window=button1) 
        but2win = canvas.create_window (x,y-20,anchor=W,window=button2)
        
        # Hide the 2nd button if we don't need it for this particular switch
        if not two_way: canvas.itemconfigure(but2win,state='hidden')
        if not two_way: canvas.itemconfigure(but1win,anchor=CENTER )

        # Compile a dictionary of everything we need to track
        new_switch = {"canvas" : canvas,               # canvas object
                      "button1" : button1,             # drawing object
                      "button2" : button2,             # drawing object
                      "bgactive" : bg_active,
                      "bginactive" :bg_inactive,
                      "fgactive" : fg_active,
                      "fginactive" : fg_inactive,
                      "switch1" : False,     
                      "switch2" : False }

        # Add the new switch to the dictionary of switches
        switches[str(switch_id)] = new_switch 
        
    return()

# -------------------------------------------------------------------------
# Externally called function to Return the current state of the switch
# -------------------------------------------------------------------------

def switch_active (switch_id:int, button_id:int=1):

    global switches # the dictionary of switches

    # Validate the switch exists
    if not switch_exists(switch_id):
        print ("ERROR: switch_active - switch "+str(switch_id)+" does not exist")
        switched = False
    else:   
        # get the switch that we are interested in
        switch = switches[str(switch_id)]
        #validate the button exists
        if str("button"+str(button_id)) not in switch.keys():
            print ("ERROR: switch_actives - button "+str(button_id)+
                   " does not exist for switch "+str(switch_id))
            switched = False
        else:
            switched = switch["switch"+str(button_id)]
        
    return(switched)

# -------------------------------------------------------------------------
# Externally called functions to Set and Clear a Switch
# -------------------------------------------------------------------------

def set_switch (switch_id:int,button_id:int=1):

    # Validate the switch exists
    if not switch_exists(switch_id):
        print ("ERROR: set_switch - switch "+str(switch_id)+" does not exist")
    elif not switch_active(switch_id,button_id):
        toggle_switch (switch_id,button_id)
    return()

def clear_switch (switch_id:int,button_id:int=1):
    # Validate the switch exists
    if not switch_exists(switch_id):
        print ("ERROR: clear_switch - switch "+str(switch_id)+" does not exist")
    if switch_active(switch_id,button_id):
        toggle_switch (switch_id,button_id)
    return()


###############################################################################

