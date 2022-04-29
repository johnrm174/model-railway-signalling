#----------------------------------------------------------------------
# This programme will eventually be a schematic editor
# ---------------------------------------------------------------------

from tkinter import *
from . import schematic
from . import menubar
from . import objects

#------------------------------------------------------------------------------------
# This is where the code begins
#------------------------------------------------------------------------------------
    
# Create the Main Root Window 
root = Tk()
root.title("Schematic Editor")
# Create the menubar (with areference to the mode selection callback)
menubar = menubar.main_menubar(root)               
canvas = schematic.create_canvas(root)
objects.set_canvas(canvas)
root.mainloop()

####################################################################################
