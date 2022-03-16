#------------------------------------------------------------------------------------
# This module contains all the functions to process menubar selections
#------------------------------------------------------------------------------------

from tkinter import *
from . import schematic

#------------------------------------------------------------------------------------
# Function to validate an entry against integer type and max/min values
#------------------------------------------------------------------------------------

def validate_entry(EB,entry,minvalue,maxvalue):
    try:
        width = int(entry.get())
    except:
        error_msg = "Entry is invalid"
    else:
        if width < minvalue or width > maxvalue:
            error_msg = "Entry is out of range"
        else:
            EB.config(fg='black')
            return(True,"")
    EB.config(fg='red')
    return(False,error_msg)
                
#------------------------------------------------------------------------------------
# Classes for Editing (and applying) the canvas settings
#------------------------------------------------------------------------------------

class canvas_element:
    def __init__(self,parent,label1,label2,initialvalue,minvalue,maxvalue):
        # Max and min values to validate the entry against
        self.min = minvalue
        self.max = maxvalue
        # Create a frame for the widgets that make up the element
        self.frame = Frame(parent)
        self.frame.pack()
        # Element comprises of Label, Entry Box and second Label
        self.label1 = Label(self.frame,text=label1)
        self.label1.pack(padx=5,pady=5,side=LEFT)
        self.entry = StringVar(parent,str(initialvalue))        
        self.value = StringVar(parent,str(initialvalue))
        self.EB = Entry(self.frame,width=5,textvariable=self.entry)
        self.EB.pack(padx=5,pady=5,side=LEFT)
        self.label2 = Label(self.frame,text=label2)
        self.label2.pack(padx=5, pady=5, side=LEFT)
        # Bind the Events associated with the Entry Box
        self.EB.bind('<Return>',self.entry_box_updated)
        self.EB.bind('<Escape>',self.entry_box_cancel)
        self.EB.bind('<FocusOut>',self.entry_box_updated)
    def entry_box_updated(self,event):
        # Validate tge entry against the pre-defined max/min values
        valid, error_msg = validate_entry(self.EB,self.entry,self.min,self.max)
        # If valid, then set the "Value" Element to reflect the new value
        if valid:
            self.value.set(self.entry.get())
            if event.keysym == 'Return': self.frame.focus()
        else:
            print (error_msg) ##########################################               
        return()
    def entry_box_cancel(self,event):
        self.entry.set(self.value.get())
        self.frame.focus()
        return()
    
class edit_canvas_settings:
    def __init__(self,root,canvas):
        # Creatre the canvas settings window
        self.canvas = canvas
        winx = root.winfo_rootx() + 150
        winy = root.winfo_rooty() + 50
        self.window = Toplevel(root)
        self.window.geometry(f'+{winx}+{winy}')
        self.window.title("Canvas Settings")
        self.window.attributes('-topmost',True)
        # Create the entry box elements for the width and height
        self.width = canvas_element(self.window,"Canvas width:","(pixels 400-4000)",
                initialvalue=self.canvas.getvar(name ="canvasx"),minvalue=400,maxvalue=4000)
        self.height = canvas_element(self.window,"Canvas height:","(pixels 200-2000)",
                initialvalue=self.canvas.getvar(name ="canvasy"),minvalue=200,maxvalue=2000)
        # Create the buttons for applying the changes
        frame = Frame(self.window)
        frame.pack()
        button1 = Button (frame, text = "Apply", command = lambda:self.resize_canvas(False))
        button1.pack(padx=5, pady=5, side=LEFT)
        button2 = Button (frame, text = "Ok", command = lambda:self.resize_canvas(True))
        button2.pack(padx=5, pady=5, side=LEFT)
        button3 = Button (frame, text = "Cancel", command = self.cancel_resize)
        button3.pack(padx=5, pady=5, side=LEFT)
    def resize_canvas(self,close_window:bool):
        # Validate the current entry box values  
        valid1, error_msg = validate_entry(self.width.EB,self.width.entry,400,4000)
        if valid1: self.width.value.set(self.width.entry.get())
        valid2, error_msg = validate_entry(self.height.EB,self.height.entry,200,2000)
        if valid2: self.height.value.set(self.height.entry.get())
        # Only allow the changes to be applied / window closed if both values are valid
        if valid1 and valid2:
            width, height = self.width.value.get(), self.height.value.get()
            self.canvas.setvar(name ="canvasx", value = int(width))
            self.canvas.setvar(name ="canvasy", value = int(height))
            self.canvas.config (width = width, height = height, scrollregion=(0,0,width,height))
            schematic.draw_grid()
            self.canvas.pack()
            if close_window: self.window.destroy()
        return()
    def cancel_resize(self,event=None):
        self.window.destroy()
        return()
    
#############################################################################################