#------------------------------------------------------------------------------------
# This module contains all the functions to process menubar selections
#------------------------------------------------------------------------------------

from tkinter import *
from . import schematic

#------------------------------------------------------------------------------------
# The Root Window and Canvas are "global" - assigned when created by the main programme
#------------------------------------------------------------------------------------

def initialise(root_object,canvas_object):
    global root, canvas
    root, canvas = root_object, canvas_object
    return()

#------------------------------------------------------------------------------------
# Dialogue and callbacks for resizing the canvas
#------------------------------------------------------------------------------------

def canvas_settings():

    def resize_canvas(event=None):
        try:
            # Get the values for the new canvas width and height
            width, height = int(entry1.get()), int(entry2.get())
        except:
            # If its not an integer then we catch the exception here
            return()
        else:
            # Do some additional validation on the values before applying
            if width < 400 or height < 200 or width > 4000 or height > 2000:
                return()
            else:
                root.setvar(name ="canvasx", value = width)
                root.setvar(name ="canvasy", value = height)
                canvas.config (width = width, height = height, scrollregion=(0,0,width,height))
                schematic.draw_grid()
                canvas.pack()
                dialog_window.destroy()
        return()
    
    def cancel_resize(event=None):
        dialog_window.destroy()
        return()

    # Creatre the basic window
    win_x = root.winfo_rootx() + 300
    win_y = root.winfo_rooty() + 100
    dialog_window=Toplevel(root)
    dialog_window.geometry(f'+{win_x}+{win_y}')
    dialog_window.title("Canvas")
    dialog_window.attributes('-topmost',True)
    # Now add the specific contents we need
    label1 = Label(dialog_window,text = "Canvas width:")
    label1.grid(row=0, column=0, padx=5, pady=5)
    entry1 = Entry(dialog_window,width=5)
    entry1.grid(row=0, column=1, padx=5, pady=5)
    entry1.insert(0,root.getvar(name="canvasx"))
    label2 = Label(dialog_window,text = "(pixels 400-4000)")
    label2.grid(row=0, column=2, padx=5, pady=5)
    label3 = Label(dialog_window,text = "Canvas height:")
    label3.grid(row=1, column=0, padx=5, pady=5)
    entry2 = Entry(dialog_window,width=5)
    entry2.grid(row=1, column=1, padx=5, pady=5)
    entry2.insert(0,root.getvar(name="canvasy"))
    label4 = Label(dialog_window,text = "(pixels 200-2000)")
    label4.grid(row=1, column=2, padx=5, pady=5)
    # Finally the buttons for applying the changes
    button1 = Button (dialog_window, text = "Ok", command = resize_canvas)
    button1.grid(row=2, column=1, padx=5, pady=5)
    button2 = Button (dialog_window, text = "Cancel", command = cancel_resize)
    button2.grid(row=2, column=2, padx=5, pady=5)
    dialog_window.bind('<Return>',resize_canvas)
    dialog_window.bind('<Escape>',cancel_resize)
    return()


#############################################################################################