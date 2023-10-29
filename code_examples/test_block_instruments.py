#------------------------------------------------------------------------------------
# This programme provides a simple example of creating and using paired block instruments
# to communicate between signal bocxes on a layout. For a more representitive configuration
# refer to the networked example ('test_networking_1.py' and 'test_networking_2.py')
#------------------------------------------------------------------------------------

from tkinter import *
import logging

# The following should enable this module to correctly import the model_railway_signals
# package from the folder above if you have just cloned/downloaded the git hub repo
# rather than installing the model_railway_signals package
import sys
sys.path.append("..")
from model_railway_signals import *

#------------------------------------------------------------------------------------
# This is for processing callbacks
#------------------------------------------------------------------------------------

def process_callbacks(item_id,callback_type):
    print ("Callback into main program - Item: "+str(item_id)+" - Callback Type: "+str(callback_type))
    print("Block Section Ahead of "+str(item_id)+" CLEAR: ",block_section_ahead_clear(item_id))
    return()

#------------------------------------------------------------------------------------
# This is where the code begins
#------------------------------------------------------------------------------------

logging.basicConfig(format='%(levelname)s: %(message)s',level=logging.DEBUG) 

print ("Creating Window and Canvas")
window = Tk()
window.title("Block Instruments Example")
canvas = Canvas(window,height=800,width=600,bg="grey85")
canvas.pack()

print ("Loading Layout State on startup")
load_layout_state()

print ("Creating Block Instruments")
create_block_instrument(canvas, 1, 150, 100, linked_to = 2,
                      bell_sound_file='bell-ring-01.wav',
                      block_callback=process_callbacks)
create_block_instrument(canvas, 2, 450, 100, linked_to = 1,
                      bell_sound_file='bell-ring-02.wav',
                      block_callback=process_callbacks)
create_block_instrument(canvas, 3, 150, 300, linked_to = 4,
                      bell_sound_file='bell-ring-03.wav',
                      block_callback=process_callbacks,
                      inst_type = instrument_type.single_line)
create_block_instrument(canvas, 4, 450, 300, linked_to = 3,
                      bell_sound_file='bell-ring-04.wav',
                      block_callback=process_callbacks,
                      inst_type = instrument_type.single_line)
create_block_instrument(canvas, 5, 150, 600, linked_to = "Box2-1")

print ("Entering Main Event Loop")
window.focus_force()
window.mainloop()

##############################################################################################################

