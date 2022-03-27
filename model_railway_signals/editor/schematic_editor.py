#----------------------------------------------------------------------
# This programme will eventually be a schematic editor
# ---------------------------------------------------------------------

from tkinter import *

from ..library import points
from ..library import signals_common
from ..library import signals_colour_lights
from ..library import signals_semaphores
from ..library import signals_ground_position
from ..library import signals_ground_disc

from . import objects
from . import schematic
from . import menubar
from . import configure_signal
from . import configure_point

#------------------------------------------------------------------------------------
# Internal Callback function up for Track Occupancy Sections events - we need to use
# this in place of the canvas callbacks as the Section Objects are Button Objects
#------------------------------------------------------------------------------------

def section_event_callback(event, object_id, event_id):
    if event_id == 0: schematic.track_cursor(event,object_id)
    elif event_id == 1: schematic.left_button_click(event,object_id)
    elif event_id == 2: schematic.right_button_click(event,object_id)
    elif event_id == 3: schematic.left_shift_click(event,object_id)
    elif event_id == 4: schematic.left_button_release(event) # Note Obj ID not needed here
    elif event_id == 5: schematic.left_double_click(event,object_id)
    return()

#------------------------------------------------------------------------------------
# Internal Callback function For the Menubar mode selection
#------------------------------------------------------------------------------------

def mode_selection(new_mode:str):
    global mode_label
    # Change the label on the menu item to show the mode selected
    new_mode_label = "Mode:"+new_mode+"  "
    mainmenubar.entryconfigure(mode_label,label = new_mode_label)
    # Make the new mode selection globally available in a Tkinter StrVar
    root.setvar(name ="mode", value = new_mode)
    # Do the mode-specific things we need to do
    if new_mode == "Edit":
        frame4.forget()
        frame3.pack(side=LEFT,expand=False,fill=BOTH)
        frame4.pack(side=LEFT,expand=True,fill=BOTH)
        schematic.display_grid()
    elif new_mode == "Run":
        frame3.forget()
        schematic.hide_grid()
        schematic.deselect_all_objects()
    elif new_mode == "Play":
        frame3.forget()
        schematic.hide_grid()
        schematic.deselect_all_objects()
        # update the global mode_label so we can find it next time
    mode_label = new_mode_label
    # Refresh all the Section objects to make them editable/non-editable depending on the mode
    for object_id in objects.schematic_objects:
        if objects.schematic_objects[object_id]["item"] == objects.object_type.section:
             objects.update_section_object(object_id)
    return()

#------------------------------------------------------------------------------------
# This is where the code begins
#------------------------------------------------------------------------------------
    
# Create the Main Root Window 
root = Tk()
root.title("Schematic Editor")

# Configure the Tkinter variables:
mode = StringVar(root, name ="mode")
root.setvar(name ="mode", value ="Edit")
# Create the menu bar
mainmenubar = Menu(root)
root.configure(menu=mainmenubar)    
# Create the various menubar items for the File Dropdown
file_menu = Menu(mainmenubar,tearoff=False)
file_menu.add_command(label = " New")
file_menu.add_command(label = " Open...")
file_menu.add_command(label = " Save")
file_menu.add_command(label = " Save as...")
file_menu.add_separator()
file_menu.add_command(label = " Quit")
mainmenubar.add_cascade(label = "File  ", menu = file_menu)
# Create the various menubar items for the Mode Dropdown
mode_label = "Mode:Edit  "
mode_menu = Menu(mainmenubar,tearoff=False)
mode_menu.add_command(label = " Edit", command=lambda x="Edit":mode_selection(x))
mode_menu.add_command(label = " Run", command=lambda x="Run":mode_selection(x))
mode_menu.add_command(label = " Play", command=lambda x="Play":mode_selection(x))
mainmenubar.add_cascade(label = mode_label, menu = mode_menu)
# Create the various menubar items for the Settings Dropdown
settings_menu = Menu(mainmenubar,tearoff=False)
settings_menu.add_command(label =" Canvas...", command = lambda:menubar.edit_canvas_settings(root,canvas))
settings_menu.add_command(label =" MQTT...")
settings_menu.add_command(label =" SPROG...")
settings_menu.add_command(label =" Files...")
mainmenubar.add_cascade(label = "Settings  ", menu = settings_menu)
# Create the various menubar items for the Help Dropdown
help_menu = Menu(mainmenubar,tearoff=False)
help_menu.add_command(label =" Help...")
help_menu.add_command(label =" About...")
mainmenubar.add_cascade(label = "Help  ", menu = help_menu)

# Create frame2 to hold the canvas, scrollbars and buttons for adding objects
frame2 = Frame(root)
frame2.pack (expand=True,fill=BOTH)

# Create frame3 inside frame2 to hold the buttons (left hand side)
frame3 = Frame (frame2, highlightthickness=1, highlightbackground="black")
frame3.pack (side=LEFT, expand=False,fill=BOTH)

#colourlight = PhotoImage(file =r"colourlight.png")
button1 = Button (frame3, text = "Draw Line", compound=TOP,
                  command=objects.create_default_line_object)
button1.pack (padx=5 ,pady=5)
#colourlight = PhotoImage(file =r"colourlight.png")
button2 = Button (frame3, text = "Colour Light", compound=TOP,
                  command=lambda:objects.create_default_signal_object
                  (signals_common.sig_type.colour_light,
                   signals_colour_lights.signal_sub_type.four_aspect))
button2.pack (padx=5, pady=5)
#semaphore = PhotoImage(file =r"semaphore.png")
button3 = Button (frame3, text = "Semaphore", compound=TOP,
                  command=lambda:objects.create_default_signal_object
                  (signals_common.sig_type.semaphore,
                   signals_semaphores.semaphore_sub_type.home))
button3.pack (padx=5, pady=5)
#groundposition = PhotoImage(file =r"semaphore.png")
button4 = Button (frame3, text = "Ground Pos",compound=TOP,
                  command=lambda:objects.create_default_signal_object
                  (signals_common.sig_type.ground_position,
                   signals_ground_position.ground_pos_sub_type.standard))
button4.pack (padx=5, pady=5)
#grounddisc = PhotoImage(file =r"semaphore.png")
button5 = Button (frame3, text = "Ground Disc", compound=TOP,
                  command=lambda:objects.create_default_signal_object
                  (signals_common.sig_type.ground_disc,
                   signals_ground_disc.ground_disc_sub_type.standard))
button5.pack (padx=5, pady=5)
#grounddisc = PhotoImage(file =r"semaphore.png")
button6 = Button (frame3, text = "Point LH", compound=TOP,
                  command=lambda:objects.create_default_point_object
                  (points.point_type.LH))
button6.pack (padx=5, pady=5)
#grounddisc = PhotoImage(file =r"semaphore.png")
button7 = Button (frame3, text = "Point RH", compound=TOP,
                  command=lambda:objects.create_default_point_object
                  (points.point_type.RH))
button7.pack (padx=5, pady=5)
#grounddisc = PhotoImage(file =r"semaphore.png")
button8 = Button (frame3, text = "Section", compound=TOP,
                  command=lambda:objects.create_default_section_object
                  (section_event_callback))
button8.pack (padx=5, pady=5)
#grounddisc = PhotoImage(file =r"semaphore.png")
button9 = Button (frame3, text = "Instrument", compound=TOP,
                  command=objects.create_default_instrument_object)
button9.pack (padx=5, pady=5)

# Create frame4 inside frame2 to hold the canvas and scrollbars (right hand side)
frame4=Frame(frame2, borderwidth = 1)
frame4.pack(side=LEFT,expand=True,fill=BOTH)

# Create the canvas and scrollbars inside frame4
canvas_width = 1000
canvas_height = 500
canvas_grid = 25
canvas=Canvas(frame4,bg="grey85",scrollregion=(0,0,canvas_width,canvas_height))
hbar=Scrollbar(frame4,orient=HORIZONTAL)
hbar.pack(side=BOTTOM,fill=X)
hbar.config(command=canvas.xview)
vbar=Scrollbar(frame4,orient=VERTICAL)
vbar.pack(side=RIGHT,fill=Y)
vbar.config(command=canvas.yview)
canvas.config(width=canvas_width,height=canvas_height)
canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
canvas.pack(side=LEFT,expand=True,fill=BOTH)
# configure the Tkinter Intvars for the width and height
canvasx = IntVar(canvas, name ="canvasx")
canvas.setvar(name ="canvasx", value = canvas_width)
canvasy = IntVar(canvas, name ="canvasy") 
canvas.setvar(name ="canvasy", value = canvas_height)
canvasgrid = IntVar(canvas, name ="gridsize")
canvas.setvar(name ="gridsize", value = canvas_grid)
# Bind the Canvas mouse and button events to the various callback functions
canvas.bind("<Motion>", schematic.track_cursor)
canvas.bind('<Button-1>', schematic.left_button_click)
canvas.bind('<Button-2>', schematic.right_button_click)
canvas.bind('<Button-3>', schematic.right_button_click)
canvas.bind('<Shift-Button-1>', schematic.left_shift_click)
canvas.bind('<ButtonRelease-1>', schematic.left_button_release)
canvas.bind('<Double-Button-1>', schematic.left_double_click)
# Bind the canvas keypresses to the associated functions
canvas.bind('<BackSpace>', schematic.delete_selected_objects)
canvas.bind('<Delete>', schematic.delete_selected_objects)
canvas.bind('<Escape>', schematic.deselect_all_objects)
canvas.bind('<Control-Key-c>', schematic.copy_selected_objects)
canvas.bind('<Control-Key-v>', schematic.paste_clipboard_objects)
canvas.bind('r', schematic.rotate_selected_objects)

objects.initialise (root, canvas)
schematic.initialise (root, canvas)

root.mainloop()

####################################################################################
