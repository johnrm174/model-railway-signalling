from tkinter import *
import interlocking
import schematic
import sections
import power_switches
import model_railway_signals 

import logging
#logging.basicConfig(format='%(levelname)s:%(funcName)s: %(message)s',level=logging.DEBUG)
logging.basicConfig(format='%(levelname)s: %(message)s',level=logging.DEBUG)

#----------------------------------------------------------------------
# Global Variables
# change these to set the initial startup conditions
#----------------------------------------------------------------------

fullScreenState = False # change to True to open as fullscreen on startup
fpl_enabled = True      # change to false to Disable FPL for simpler operation

#----------------------------------------------------------------------
# a subclass of Canvas for dealing with resizing of windows
#----------------------------------------------------------------------

class ResizingCanvas(Canvas):
    def __init__(self,parent,**kwargs):
        Canvas.__init__(self,parent,**kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()
        
    def on_resize(self,event):
        # determine the ratio of old width/height to new width/height
        wscale = event.width/self.width
        hscale = event.height/self.height
        self.width = event.width
        self.height = event.height
        # rescale all the objects
        self.scale("all", 0, 0, wscale, hscale)

# Callbacks for toggling Full screen mode
def toggleFullScreen(event):
    global window, fullScreenState
    print (str(event))
    fullScreenState = not fullScreenState
    window.attributes("-fullscreen",fullScreenState)

def quitFullScreen(event):
    global window, fullScreenState
    print (str(event))
    fullScreenState = False
    window.attributes("-fullscreen",fullScreenState)
    
#----------------------------------------------------------------------
# These are the callback functions for the Controls
#----------------------------------------------------------------------

def switch_button(switch_id,button_id):
#    print ("***** CALLBACK - Power Section Switch "+str(switch_id)+", button "+str(button_id))
    # A "track power section" switch change
    schematic.update_track_schematic(canvas) # to reflect any track power section changes
    return()

def sections_callback_function(section_id,callback_type):
#    print ("***** CALLBACK - Track Occupancy Section "+str(section_id)+" : "+str(callback_type))
    # Will be a "track occupancy" switch change 
    sections.override_signals_based_on_track_occupancy() # to reflect any manual track occupancy changes
    sections.refresh_signal_aspects() # Ensure any aspect changes are reflected back along the route
    return()

def point_callback_function(point_id,callback_type):
#    print ("***** CALLBACK - Point " + str(point_id) + " : " + str(callback_type))
    sections.override_signals_based_on_track_occupancy() # to reflect any route changes
    sections.refresh_signal_aspects() # Ensure any aspect changes are reflected back along the route
    power_switches.update_track_power_section_switches() # sections auto switched on point & signal settings
    schematic.update_track_schematic(canvas) # To reflect any route changes 
    interlocking.process_interlocking_east()
    interlocking.process_interlocking_west()
    return()

def signal_callback_function(sig_id,callback_type):
#    print ("***** CALLBACK - Signal " + str(sig_id) + " : " + str(callback_type))
    if callback_type == model_railway_signals.sig_callback_type.sig_passed:
        sections.update_track_occupancy(sig_id) # update route occupancy sections as signal is passed
        sections.override_signals_based_on_track_occupancy() # to reflect any route occupancy changes
    sections.refresh_signal_aspects() # Ensure any aspect changes are reflected back along the route
    power_switches.update_track_power_section_switches() # sections auto switched on point & signal settings
    schematic.update_track_schematic(canvas) # to reflect any track power section changes 
    interlocking.process_interlocking_east()
    interlocking.process_interlocking_west()
    return()

#------------------------------------------------------------------------------------
# This is where the code begins
#------------------------------------------------------------------------------------

# Create the Window and canvas
print ("Creating Window and Canvas")
window = Tk()
window.attributes('-fullscreen', fullScreenState)  
window.title("My Model Railway")
window.bind("<F11>", toggleFullScreen)
window.bind("<Escape>", quitFullScreen)
frame = Frame(window)
frame.pack(fill=BOTH, expand=YES)
canvas = ResizingCanvas(frame,highlightthickness=0,height=1000,width=1900)
canvas.pack(fill=BOTH, expand=YES) 

print ("Creating Layout Schematic")
# Draw the Schematic track plan (creating points as required)
# Create the Signals on the Schematic track plan
schematic.create_track_schematic(canvas,point_callback_function,fpl_enabled=fpl_enabled)
schematic.create_layout_signals(canvas,signal_callback_function)

# Create the section Switches and track occupancy switches for the layout
power_switches.create_section_switches(canvas,switch_button)
sections.create_track_occupancy_switches(canvas,sections_callback_function)

# Set the initial interlocking conditions and signal aspects
interlocking.set_initial_interlocking_conditions()
sections.refresh_signal_aspects()

print ("Entering Main Loop")
# Tag all the drawing objects to enable them to be resized when
# the window is resized and Enter the main tkinter event loop
canvas.addtag_all("all")
window.mainloop()


