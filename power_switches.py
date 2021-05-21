# --------------------------------------------------------------------------------
# This module deals with the track power sections which can be either automatically
# or manually switched. If "Manual Power Switching" (a switch on the display) is not
# active then the individual power sections (apart from the Goods Yard and MPD)
# are switched automatically depending on the routes that have been set up
#(i.e. based on the signal and point settings) 
# --------------------------------------------------------------------------------

from tkinter import *
import tkinter.font

from model_railway_signals import *

# Global variables for the track power sections

power_goods_loop = 1
power_branch_platform = 2
power_up_platform = 3
power_down_loop = 4
power_down_platform = 5
power_branch_west = 6
power_branch_east = 7
power_goods_yard = 8
power_mpd = 9
power_switch_override = 10

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
                switch["button1"].config(relief="raised",bg="SeaGreen3",fg="black",
                                activebackground="SeaGreen3", activeforeground="black")
            else:  # Switch is off
                # Activate the Button
                switch["switch1"] = True
                switch["button1"].config(relief="sunken",bg="SeaGreen1",fg="black",
                                activebackground="SeaGreen1", activeforeground="black")
                # De-activate the other button
                switch["switch2"] = False
                switch["button2"].config(relief="raised",bg="SeaGreen3",fg="black",
                                activebackground="SeaGreen3", activeforeground="black")

        elif button_id == 2:
            if switch["switch2"] == True:  # Switch is on
                switch["switch2"] = False
                switch["button2"].config(relief="raised",bg="SeaGreen3",fg="black",
                                activebackground="SeaGreen3", activeforeground="black")
            else:  # Switch is off
                # Activate the Button
                switch["switch2"] = True
                switch["button2"].config(relief="sunken",bg="SeaGreen1",fg="black",
                                activebackground="SeaGreen1", activeforeground="black")
                # De-activate the other button
                switch["switch1"] = False
                switch["button1"].config(relief="raised",bg="SeaGreen3",fg="black",
                                activebackground="SeaGreen3", activeforeground="black")

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
                   label1:str="", label2:str="", two_way:bool=False):
    
    global switches # the dictionary of switches
    # also uses fontsize, xpadding, ypadding imported from "common"

    # Verify that a switch with the same ID does not already exist
    if switch_exists(switch_id):
        print ("ERROR: create_switch - switch ID "+str(switch_id)+" already exists")
    elif switch_id < 1:
        print ("ERROR: create_switch - switch ID must be greater than zero")
    else: # we're good to go on and create the switch
        
        # set the font size for the buttons
        myfont = tkinter.font.Font(size=8)

        # Create the button objects and their callbacks
        button1 = Button (canvas,text=label1,state="normal",
                    padx=3,pady=3,
                    relief="raised", font=myfont, bg="SeaGreen3", fg="black",
                    activebackground="SeaGreen3", activeforeground="black",
                    command = lambda:toggle_switch(switch_id,1,switch_callback))
        button2 = Button (canvas,text=label2,state="normal",padx=3,pady=3,
                    relief="raised", font=myfont, bg="SeaGreen3", fg="black",
                    activebackground="SeaGreen3", activeforeground="black",
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

#----------------------------------------------------------------------
# Externally called Function to create (and display) the track power
# section  on the schematic. 
#----------------------------------------------------------------------

def create_section_switches(canvas, switch_callback):

    global power_goods_loop, power_branch_platform, power_up_platform
    global power_down_loop, power_down_platform, power_branch_west, power_branch_east
    global power_goods_yard, power_mpd, power_switch_override
    
    create_switch (canvas, power_switch_override, 200,50,label1="Manual Power Switching",switch_callback=switch_callback)
    create_switch (canvas, power_goods_loop, 900,385,two_way=True, label1="Loop LH", label2="Loop RH",switch_callback=switch_callback)
    create_switch (canvas, power_branch_platform, 900,510,two_way=True, label1="Plat 3 LH", label2="Plat 3 RH",switch_callback=switch_callback)
    create_switch (canvas, power_up_platform, 750,550,label1="Up Main", switch_callback=switch_callback)
    create_switch (canvas, power_down_loop, 1050,600,label1="Down Main",switch_callback=switch_callback)
    create_switch (canvas, power_down_platform, 1050,650,label1="Platform 1",switch_callback=switch_callback)
    create_switch (canvas, power_branch_west, 255,485,two_way=True, label1="Branch",label2="Local",switch_callback=switch_callback)
    create_switch (canvas, power_branch_east, 1615,485,two_way=True, label1="Branch",label2="Local",switch_callback=switch_callback)
    create_switch (canvas, power_goods_yard, 750,250,label1="Goods Yard",switch_callback=switch_callback)
    create_switch (canvas, power_mpd, 500,350,label1="MPD",switch_callback=switch_callback)

    return()

#----------------------------------------------------------------------
# Externally called Function to automatically switch the track power
# sections based on the signal settings. If "Manual Power Switching"
# is not selected then the individual power sections (apart from the Goods
# Yard and MPD) are switched automatically depending on the routes that
# have been set up (i.e. based on the signal and point settings) 
#----------------------------------------------------------------------

def update_track_power_section_switches():

    global power_goods_loop, power_branch_platform, power_up_platform
    global power_down_loop, power_down_platform, power_branch_west, power_branch_east
    global power_goods_yard, power_mpd, power_switch_override

    # Only Switch if automatic switching is enabled
    if not switch_active (power_switch_override):

        # Auto switch the Down loop power section
        if signal_clear(12):
            set_switch (power_down_loop)
        elif signal_clear(11) and not point_switched(9) and not point_switched(7):
            set_switch (power_down_loop)
        else:
            clear_switch (power_down_loop)
            
        # Auto switch the Down Platform power section
        if signal_clear(13):
            set_switch (power_down_platform)
        elif signal_clear(11) and not point_switched(9) and point_switched(7):
            set_switch (power_down_platform)
        else:
            clear_switch (power_down_platform)
            
        # Auto switch the Up Platform power section
        if signal_clear(4):
            set_switch (power_up_platform)
        elif signal_clear(3) and not point_switched(2):
            set_switch (power_up_platform)
        else:
            clear_switch (power_up_platform)

        # Auto switch the LH Branch Headshunt power section
        if signal_clear(1) or signal_clear(2):
            set_switch(power_branch_west,1)
        elif (signal_clear(5) or signal_clear (6)) and not point_switched(2):
            set_switch(power_branch_west,1)
        elif subsidary_clear(2) or subsidary_clear(6):
            set_switch(power_branch_west,2)
        elif subsidary_clear(5) and point_switched(4) and not point_switched(5):
            set_switch(power_branch_west,2)
        else:
            clear_switch (power_branch_west,1)
            clear_switch(power_branch_west,2)
            
        # Auto switch the RH Branch Headshunt power section
        if signal_clear(9) or signal_clear(10):
            set_switch(power_branch_east,1)
        elif (signal_clear(7) or signal_clear (8)) and not point_switched(8):
            set_switch(power_branch_east,1)
        elif subsidary_clear(10) or subsidary_clear(8):
            set_switch(power_branch_east,2)
        elif subsidary_clear(7) and point_switched(6):
            set_switch(power_branch_east,2)
        else:
            clear_switch(power_branch_east,1)
            clear_switch(power_branch_east,2)
            
        # Auto switch the Goods Loop power section - LH side first
        if signal_clear(15) or signal_clear(14) or signal_clear(5) or subsidary_clear(5):
            set_switch(power_goods_loop,1)
        elif (signal_clear(2) or subsidary_clear(2)) and point_switched(4):
            set_switch(power_goods_loop,1)
        elif signal_clear(3) and point_switched(2) and point_switched(4): 
            set_switch(power_goods_loop,1)
        # Deal with RH side 
        elif signal_clear(16) or signal_clear(7) or subsidary_clear(7):
            set_switch(power_goods_loop,2)
        elif (signal_clear(10) or subsidary_clear(10)) and point_switched(6):
            set_switch(power_goods_loop,2)
        elif signal_clear(11) and point_switched(9) and point_switched(6):
            set_switch(power_goods_loop,2)
        else:
            clear_switch(power_goods_loop,1)
            clear_switch(power_goods_loop,2)
            
        # Auto switch the Platform 3 power section - LH side first
        if signal_clear(6) or subsidary_clear(6):
            set_switch(power_branch_platform,1)
        elif (signal_clear(2) or subsidary_clear(2)) and not point_switched(4):
            set_switch(power_branch_platform,1)
        elif signal_clear(3) and point_switched(3) and not point_switched(4): 
            set_switch(power_branch_platform,1)
        # Deal with RH side 
        elif signal_clear(8) or subsidary_clear(8):
            set_switch(power_branch_platform,2)
        elif (signal_clear(10) or subsidary_clear(10)) and not point_switched(6):
            set_switch(power_branch_platform,2)
        elif signal_clear(11) and point_switched(9) and not point_switched(6):
            set_switch(power_branch_platform,1)
        else:
            clear_switch(power_branch_platform,1)
            clear_switch(power_branch_platform,2)

    return()
###############################################################################

