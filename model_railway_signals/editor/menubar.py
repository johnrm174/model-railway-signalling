#------------------------------------------------------------------------------------
# This module contains all the functions to process menubar selections
#------------------------------------------------------------------------------------

from tkinter import *
from . import schematic
from . import common
                
#------------------------------------------------------------------------------------
# Class for a canvas size element (width or height)
#------------------------------------------------------------------------------------

class canvas_element:
    def __init__(self, parent_window, label, tooltip, minvalue, maxvalue):
        # The default tooltip for the entry box
        self.tooltip = tooltip
        # Max and min values to validate the entry against
        self.min = minvalue
        self.max = maxvalue
        # Create a frame for the widgets that make up the element
        self.frame = Frame(parent_window)
        self.frame.pack()
        # Element comprises of Label and Entry Box (with tooltip)
        self.label = Label(self.frame, text=label)
        self.label.pack(padx=2,pady=2, side=LEFT)
        self.entry = StringVar(self.frame)        
        self.value = StringVar(self.frame)
        self.EB = Entry(self.frame, width=5, textvariable=self.entry)
        self.EB.pack(padx=2, pady=2, side=LEFT)
        self.TT = common.CreateToolTip(self.EB, tooltip)
        # Bind the Events associated with the Entry Box
        self.EB.bind('<Return>',self.entry_box_updated)
        self.EB.bind('<Escape>',self.entry_box_cancel)
        self.EB.bind('<FocusOut>',self.entry_box_updated)
        
    def validate(self):
        try:
            width = int(self.entry.get())
        except:
            self.TT.text = "Not a valid integer"
        else:
            if width < self.min or width > self.max:
                self.TT.text = ("Out of range - value must be "+
                        "between "+str(self.min)+" and "+str(self.max))
            else:
                self.EB.config(fg='black')
                self.TT.text = self.tooltip
                self.value.set(self.entry.get())
                return(True)
        self.EB.config(fg='red')
        return(False)

    def entry_box_updated(self,event):
        valid = self.validate()
        if event.keysym == 'Return': self.frame.focus()
    
    def entry_box_cancel(self,event):
        self.entry.set(self.value.get())
        self.frame.focus()

#------------------------------------------------------------------------------------
# Class for the Canvas configuration toolbar window
#------------------------------------------------------------------------------------
    
class edit_canvas_settings:
    def __init__(self,root,canvas):
        # Creatre the top level window for the canvas settings
        self.canvas = canvas
        winx = root.winfo_rootx() + 150
        winy = root.winfo_rooty() + 50
        self.window = Toplevel(root)
        self.window.geometry(f'+{winx}+{winy}')
        self.window.title("Canvas Settings")
        self.window.attributes('-topmost',True)
        # Create the entry box elements for the width and height
        self.width = canvas_element(self.window,"Canvas width:",
                "Enter width in pixels (400-4000)", 400, 4000)
        self.height = canvas_element(self.window,"Canvas height:",
                "Enter height in pixels (200-2000)", 200, 2000)
        # Create the common Apply/OK/Reset/Cancel buttons for the window
        common.window_controls(self.window, self, self.load_state, self.save_state)
        # Load the initial UI state
        self.load_state()

    def load_state(self, parent_object=None):
        self.width.entry.set(self.canvas.getvar(name ="canvasx"))
        self.width.value.set(self.canvas.getvar(name ="canvasx"))
        self.height.entry.set(self.canvas.getvar(name ="canvasy"))
        self.height.value.set(self.canvas.getvar(name ="canvasy"))
        self.width.validate()
        self.height.validate()
        
    def save_state(self, parent_object, close_window:bool):
        # Only allow the changes to be applied / window closed if both values are valid
        if self.width.validate() and self.height.validate():
            width, height = self.width.value.get(), self.height.value.get()
            # Resize the canvas
            self.canvas.setvar(name ="canvasx", value = int(width))
            self.canvas.setvar(name ="canvasy", value = int(height))
            self.canvas.config (width=width, height=height, scrollregion=(0,0,width,height))
            self.canvas.pack()
            # redraw the grid
            schematic.draw_grid()
            # close the window (on OK or cancel)
            if close_window: self.window.destroy()
        
#############################################################################################
