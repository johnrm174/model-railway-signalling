from model_railway_signals import *
import power_switches

# The default colours for the schematic
off_colour = "grey75" # sections that are switched off
local_colour = "orange"
branch_colour="yellow"
up_colour="red"
down_colour="green"

# The default values for the global lists of drawing objects
# These are the drawing objects we need to track as we need to
# change the colours based on point and power section settings.
lh_auto_sec1 = [0]
lh_auto_sec2 = [0]
lh_auto_sec3 = [0]
rh_auto_sec1 = [0]
rh_auto_sec2 = [0]
rh_auto_sec3 = [0]
platform1 = [0]
platform2 = [0]
platform3  = [0]
through_loop = [0]
goods_loop  = [0]
rh_headshunt = [0]
lh_headshunt = [0]
goods_yard = [0]
point10 = [0]
point12 = [0]
point13 = [0]
point14 = [0]
point15 = [0]
point16 = [0]
point17 = [0]
siding1 = [0]
siding2 = [0]
siding3 = [0]
siding4 = [0]
siding5 = [0]
siding6 = [0]
siding7 = [0]
siding8 = [0]
mpd = [0]
point20 = [0]
point21 = [0]
point22 = [0]
point23 = [0]
mpd1 = [0]
mpd2 = [0]
mpd3 = [0]
mpd4 = [0]
mpd5 = [0]
mpd6 = [0]

#------------------------------------------------------------------------------------
# Externally called Function to create the schematic diagram (including the points)
# This function calls the points package to create points as required.
# All the other lines are drawn via tkinter
#------------------------------------------------------------------------------------

def create_track_schematic (canvas, point_callback, fpl_enabled:bool=True):

    # Global baseline colour definition (everything else inherits from these)
    global up_colour, down_colour, branch_colour, local_colour, off_colour

    # Global drawing objects for the main station schematic
    global platform1, platform2, platform3, through_loop, goods_loop
    global lh_headshunt, lh_auto_sec1, lh_auto_sec2, lh_auto_sec3
    global rh_headshunt, rh_auto_sec1, rh_auto_sec2, rh_auto_sec3
    
    # Global drawing objects for the Goods Yard Schematic
    global goods_yard, point10, point12, point13, point14, point15, point16, point17
    global siding1, siding2, siding3, siding4, siding5, siding6, siding7, siding8

    # Global drawing objects for the MPD Schematic
    global mpd, point20, point21, point22, point23, mpd1, mpd2, mpd3, mpd4, mpd5, mpd6

    #------------------------------------------------------------------------------------
    # Draw the Goods Yard
    #------------------------------------------------------------------------------------

    # Goods yard LH headshunt
    lines1 = [canvas.create_line(450,240,450,260,fill=off_colour,width=3)] # End stop
    lines2 = [canvas.create_line(450,250,575,250,fill=off_colour,width=3)]  # up to point 5
    lines3 = create_point (canvas,5,point_type.RH,600,250,off_colour,also_switch=105,
                point_callback=point_callback)
    lines4 = [canvas.create_line(625,250,875,250,fill=off_colour,width=3)]  # from point 5 to point 18
    lines5 = [canvas.create_line(600,275,700,375,fill=off_colour,width=3)]  # from point 5 to point 105
    lines6 = create_point (canvas,18,point_type.LH,900,250,off_colour,
                point_callback=point_callback)

    # Goods yard RH headshunt
    lines7 = create_point (canvas,110,point_type.RH,1225,400,off_colour,auto=True,
                orientation=180, point_callback=point_callback)
    lines8 = [canvas.create_line(1250,400,1500,400,fill=off_colour,width=3)] # point 101 Headshunt
    lines9 = [canvas.create_line(1500,390,1500,410,fill=off_colour,width=3)] # End stop

    goods_yard = lines1 + lines2 + lines3 + lines4 + lines5 + lines6 + lines7 + lines8 + lines9

    # Draw the sidings - all are switchable depending on the point settings
    siding1 = [canvas.create_line(900,225,1075,50,fill=off_colour,width=3), # point 18 siding
               canvas.create_line(1068,43,1082,57,fill=off_colour,width=3)] # End stop

    lines1 = [canvas.create_line(925,250,975,250,fill=off_colour,width=3)] # point 18 to point 14
    lines2 = create_point (canvas,14,point_type.LH,1000,250,off_colour,
                point_callback=point_callback)
    point14 = lines1 + lines2
    
    lines1 = [canvas.create_line(1025,250,1100,250,fill=off_colour,width=3)] # point 14 to point 13
    lines2 = create_point (canvas,13,point_type.RH,1125,250,off_colour,
                point_callback=point_callback)
    point13 = lines1 + lines2

    # Top ladder of sidings
    
    lines1 = [canvas.create_line(1000,225,1025,200,fill=off_colour,width=3)] # point 14 to point 15
    lines2 = create_point (canvas,15,point_type.LH,1050,200,off_colour,
                point_callback=point_callback)
    point15 = lines1 + lines2
    
    lines1 = [canvas.create_line(1050,175,1075,150,fill=off_colour,width=3)] # point 15 to point 16
    lines2 = create_point (canvas,16,point_type.LH,1100,150,off_colour,
                point_callback=point_callback)
    point16 = lines1 + lines2

    lines1 = [canvas.create_line(1100,125,1125,100,fill=off_colour,width=3)] # point 16 to point 17
    lines2 =create_point (canvas,17,point_type.LH,1150,100,off_colour,
                point_callback=point_callback)
    point17 = lines1 + lines2

    lines1 = [canvas.create_line(1150,75,1175,50,fill=off_colour,width=3)] # point 17 to top siding
    lines2 = [canvas.create_line(1175,50,1500,50,fill=off_colour,width=3)] # top siding
    lines3 = [canvas.create_line(1500,40,1500,60,fill=off_colour,width=3)] # End stop
    siding2 = lines1 + lines2 + lines3

    siding3 = [canvas.create_line(1175,100,1500,100,fill=off_colour,width=3),
               canvas.create_line(1500,90,1500,110,fill=off_colour,width=3)] # End stop
    
    siding4 = [canvas.create_line(1125,150,1500,150,fill=off_colour,width=3), # point 16 siding
               canvas.create_line(1500,140,1500,160,fill=off_colour,width=3)] # End stop
    
    siding5 = [canvas.create_line(1075,200,1500,200,fill=off_colour,width=3), # point 15 siding
               canvas.create_line(1500,190,1500,210,fill=off_colour,width=3)] # End stop

    # Bottom ladder of sidings
    
    siding6 =  [canvas.create_line(1150,250,1500,250,fill=off_colour,width=3), # point 13 siding
                canvas.create_line(1500,240,1500,260,fill=off_colour,width=3)] # End stop

    lines1 = [canvas.create_line(1125,275,1150,300,fill=off_colour,width=3)] # point 13 to point 12
    lines2 = create_point (canvas,12,point_type.RH,1175,300,off_colour,
                point_callback=point_callback)
    point12 = lines1 + lines2
    
    lines1 = [canvas.create_line(1175,325,1200,350,fill=off_colour,width=3)] # point 12 to point 11
    lines2 = create_point (canvas,10,point_type.RH,1225,350,off_colour, also_switch=110,
                point_callback=point_callback)
    point10 = lines1 + lines2

    siding7 = [canvas.create_line(1200,300,1500,300,fill=off_colour,width=3), # point 12 siding
               canvas.create_line(1500,290,1500,310,fill=off_colour,width=3)] # End stop

    siding8 = [canvas.create_line(1250,350,1500,350,fill=off_colour,width=3), # point 10 siding
               canvas.create_line(1500,340,1500,360,fill=off_colour,width=3)] # End stop

    #------------------------------------------------------------------------------------
    # Draw the Motive Power Depot
    #------------------------------------------------------------------------------------

    lines1 = [canvas.create_line(500,400,625,400,fill=off_colour,width=3)]  # point 19 to point 4
    lines2 = create_point(canvas,19,point_type.RH,475,400,off_colour,
                        orientation=180, point_callback=point_callback)
    mpd = lines1 + lines2  # The Main MPD Section 
    
    mpd1 = [canvas.create_line(475,375,325,225,fill=off_colour,width=3), # point 19 siding
              canvas.create_line(318,232,332,218,fill=off_colour,width=3)] # End stop
    
    lines1 = [canvas.create_line(425,400,450,400,fill=off_colour,width=3)]  # point 20 to point 19
    lines2 = create_point(canvas,20,point_type.RH,400,400,off_colour,
                        orientation=180, point_callback=point_callback)
    point20 = lines1 + lines2
    
    lines1 = create_point(canvas,21,point_type.RH,275,400,off_colour,
                        orientation=180, point_callback=point_callback)
    lines2 = [canvas.create_line(300,400,375,400,fill=off_colour,width=3)] # point 21 to point 20
    point21 = lines1 + lines2
    
    mpd6 = [canvas.create_line(100,400,250,400,fill=off_colour,width=3), # point 21 siding 1
            canvas.create_line(100,390,100,410,fill=off_colour,width=3)] # End stop

    mpd5 = [canvas.create_line(275,375,250,350,fill=off_colour,width=3),
            canvas.create_line(100,350,250,350,fill=off_colour,width=3), # point 21 siding 2
            canvas.create_line(100,340,100,360,fill=off_colour,width=3)] # End stop

    lines1 = create_point(canvas,22,point_type.RH,300,300,off_colour,
                        orientation=180, point_callback=point_callback)
    lines2 = [canvas.create_line(400,375,325,300,fill=off_colour,width=3)] 
    point22 = lines1 + lines2
    
    mpd2 = [canvas.create_line(300,275,200,175,fill=off_colour,width=3), # point 22 siding
              canvas.create_line(193,182,207,168,fill=off_colour,width=3)] # End stop
    canvas.create_oval (200,175,250,225, width=3, outline=off_colour)


    lines1 = create_point(canvas,23,point_type.RH,225,300,off_colour,
                        orientation=180, point_callback=point_callback)
    lines2 = [canvas.create_line(250,300,275,300,fill=off_colour,width=3)] 
    point23 = lines1 + lines2

    mpd4 = [canvas.create_line(100,300,200,300,fill=off_colour,width=3), # point 23 siding 1
            canvas.create_line(100,290,100,310,fill=off_colour,width=3)] # End stop

    mpd3 = [canvas.create_line(225,275,200,250,fill=off_colour,width=3),
            canvas.create_line(100,250,200,250,fill=off_colour,width=3), # point 23 siding 2
            canvas.create_line(100,240,100,260,fill=off_colour,width=3)] # End stop

    #------------------------------------------------------------------------------------
    # Draw the Goods loop and associated auto sections
    #------------------------------------------------------------------------------------
    
    # LH auto section #3 (on goods loop)
    lines1 = create_point(canvas,4,point_type.LH,650,400,off_colour,fpl=fpl_enabled, also_switch=104,
                        orientation=180, point_callback=point_callback)
    # Point return comprises: [straight blade, switched blade, straight route ,switched route]
    lh_auto_sec3 = lines1
    
    # Goods loop (switchable between rh and lh auto sections)
    lines1 = create_point (canvas,105,point_type.RH,700,400,off_colour, auto=True, orientation=180)
    lines2 = [canvas.create_line(725,400,1150,400,fill=off_colour,width=3)]  # point 105 to point 6
    # Point return comprises: [straight blade, switched blade, straight route ,switched route]
    goods_loop = lines1 + lines2

    # RH auto section #3 (on goods loop)
    lines1 = create_point (canvas,6,point_type.RH,1175,400,off_colour,fpl=fpl_enabled,also_switch=106,
                point_callback=point_callback)
    # Point return comprises: [straight blade, switched blade, straight route ,switched route]
    rh_auto_sec3 = lines1

    #------------------------------------------------------------------------------------
    # Draw the BRANCH Line
    #------------------------------------------------------------------------------------

    # lh Branch line route (objects that are never going to change colour)
    canvas.create_line(0,500,175,500,fill=branch_colour,width=3) # End of canvas to  signal 1

    # Right Hand headshunt
    lines1 = [canvas.create_line(175,500,525,500,fill=off_colour,width=3)] # signal 1 to point 102
    lh_headshunt = lines1
    
    # draw lh auto section #2(on branch-line)
    lines1 = create_point (canvas,102,point_type.LH,550,500,off_colour,auto=True,orientation=180)
    lines2 = [canvas.create_line(575,500,625,450,fill=off_colour,width=3)] # Point 102 to Point 104
    lines3 = create_point (canvas,104,point_type.LH,650,450,off_colour,auto=True)
    # Point return comprises: [straight blade, switched blade, straight route ,switched route]
    lh_auto_sec2 = lines1 + lines2 + lines3

    # Branch platform (switchable between rh and lh auto sections)
    lines1 = [canvas.create_line(675,450,1150,450,fill=off_colour,width=3)]  # point 104 to point 106
    platform3 = lines1
    
    # draw rh auto section #2(on branch-line)
    lines1 = create_point (canvas,106,point_type.RH,1175,450,off_colour,auto=True,orientation=180)
    lines2 = [canvas.create_line(1200,450,1250,500,fill=off_colour,width=3)] # Point 102 to Point 104
    lines3 = create_point (canvas,108,point_type.RH,1275,500,off_colour,auto=True)
    # Point return comprises: [straight blade, switched blade, straight route ,switched route]
    rh_auto_sec2 = lines1 + lines2 + lines3

    # Right Hand headshunt
    lines1 = [canvas.create_line(1300,500,1700,500,fill=off_colour,width=3)] # point 108 to signal 9
    rh_headshunt = lines1
    
    # Branch line route (objects that are never going to change colour)
    canvas.create_line(1700,500,1900,500,fill=branch_colour,width=3) # signal 9 to end of canvas

    #------------------------------------------------------------------------------------
    # Draw the UP Line
    #------------------------------------------------------------------------------------

    # lh Up line route (objects that are never going to change colour)
    canvas.create_line(0,550,425,550,fill=up_colour,width=3) # end of canvas to point 101
    canvas.create_line(575,550,650,550,fill=up_colour,width=3) # point 2 to start of platform

    # draw lh auto section #1(on down-line)
    lines1 = create_point (canvas,101,point_type.LH,450,550,up_colour,auto=True,orientation=180)
    lines2 = [canvas.create_line(475,550,525,550,fill=up_colour,width=3)] # point 101 to point 2
    lines3 = create_point (canvas,2,point_type.LH,550,550,up_colour,fpl=fpl_enabled,also_switch=102,
                point_callback=point_callback)
    # Point return comprises: [straight blade, switched blade, straight route ,switched route]
    lh_auto_sec1 = lines1 + lines2 + lines3

    # Up line platform (switchable on/off)
    lines1 = [canvas.create_line(650,550,1150,550,fill=off_colour,width=3)]  # point 103 to point 7
    platform2 = lines1
    
    # draw rh auto section #1(on down-line)
    lines1 = create_point (canvas,8,point_type.RH,1275,550,up_colour,fpl=fpl_enabled,also_switch=108,
                orientation=180,point_callback=point_callback)
    lines2 = [canvas.create_line(1300,550,1350,550,fill=up_colour,width=3)] # point 8 to point 109
    lines3 = create_point (canvas,109,point_type.RH,1375,550,up_colour,auto=True)
    # Point return comprises: [straight blade, switched blade, straight route ,switched route]
    rh_auto_sec1 = lines1 + lines2 + lines3

    # rh Up line route (objects that are never going to change colour)
    canvas.create_line(1150,550,1250,550,fill=up_colour,width=3) # end of platform to point 8
    canvas.create_line(1400,550,1900,550,fill=up_colour,width=3) # point 109 to end of canvas

    #------------------------------------------------------------------------------------
    # Draw the DOWN Line (including the platform loop)
    #------------------------------------------------------------------------------------

    # lh Down line route (objects that are never going to change colour)
    canvas.create_line(0,600,425,600,fill=down_colour,width=3)  # end of canvas to point 1
    create_point(canvas,1,point_type.LH,450,600,down_colour,fpl=fpl_enabled,also_switch=101,
            point_callback=point_callback)

    canvas.create_line(475,600,600,600,fill=down_colour,width=3) # point 1 to point 103
    create_point(canvas,103,point_type.RH,625,600,down_colour,auto=True)
    canvas.create_line(575,640,575,660,fill=down_colour,width=3) # End stop
    canvas.create_line(575,650,600,650,fill=down_colour,width=3) # End stop to point 3

    create_point(canvas,3,point_type.RH,625,650,down_colour,fpl=fpl_enabled,also_switch=103,
                orientation=180, point_callback=point_callback)

    # Down through loop (switchable on/off)
    lines1 = [canvas.create_line(650,600,1150,600,fill=off_colour,width=3)]  # point 103 to point 7
    through_loop = lines1
    
    # Platform loop (switchable on/off)
    lines1 = [canvas.create_line(650,650,1150,650,fill=off_colour,width=3)] # point 3 to end of loop
    platform1 = lines1

    # rh Down line route (objects that are never going to change colour)
    canvas.create_line(1150,650,1175,625,fill=down_colour,width=3) # end of loop to point 7
    create_point(canvas,7,point_type.LH,1175,600,down_colour,fpl=fpl_enabled,orientation=180,
                point_callback=point_callback)
    canvas.create_line(1200,600,1350,600,fill=down_colour,width=3) # point 7 to point 9
    create_point(canvas,9,point_type.RH,1375,600,down_colour,fpl=fpl_enabled, also_switch=109,
                orientation=180,point_callback=point_callback)
    canvas.create_line(1400,600,1900,600,fill=down_colour,width=3) # point 9 to end of canvas


    return()

#----------------------------------------------------------------------
# Externally called function to create the signals for the schematic
#----------------------------------------------------------------------

def create_layout_signals(canvas, sig_callback):

    create_colour_light_signal (canvas,1,100,500,
            signal_subtype = signal_sub_type.three_aspect,
            sig_callback=sig_callback, sig_passed_button = True,
            refresh_immediately = False)
    
    create_colour_light_signal (canvas,2,475,500,
            signal_subtype = signal_sub_type.three_aspect,
            sig_callback=sig_callback, sig_passed_button = True,
            lhfeather45= True, position_light=True,
            refresh_immediately = False)
    
    create_colour_light_signal (canvas,3,400,550,
            signal_subtype = signal_sub_type.four_aspect,
            sig_callback=sig_callback, sig_passed_button = True,
            lhfeather45 = True, lhfeather90 = True,
            refresh_immediately = False)

    create_colour_light_signal (canvas,4,1050,550,
            signal_subtype = signal_sub_type.four_aspect,
            sig_callback=sig_callback, sig_passed_button = True,
            refresh_immediately = False)

    create_colour_light_signal (canvas,5,750,400,orientation=180,
            signal_subtype = signal_sub_type.three_aspect,
            sig_callback=sig_callback, sig_passed_button = True,
            lhfeather45= True, position_light=True,
            refresh_immediately = False)

    create_colour_light_signal (canvas,6,750,450, orientation=180,
            signal_subtype = signal_sub_type.three_aspect,
            sig_callback=sig_callback, sig_passed_button = True, 
            lhfeather45= True, position_light=True,
            refresh_immediately = False)

    create_colour_light_signal (canvas,7,1050,400,
            signal_subtype = signal_sub_type.three_aspect,
            sig_callback=sig_callback, sig_passed_button = True,
            rhfeather45= True, position_light=True,
            refresh_immediately = False)

    create_colour_light_signal (canvas,8,1050,450,
            signal_subtype = signal_sub_type.three_aspect,
            sig_callback=sig_callback, sig_passed_button = True,
            rhfeather45= True, position_light=True,
            refresh_immediately = False)
    
    create_colour_light_signal(canvas,9,1730,500,orientation=180,
            signal_subtype = signal_sub_type.three_aspect,
            sig_callback=sig_callback, sig_passed_button = True,
            refresh_immediately = False)

    create_colour_light_signal (canvas,10,1400,500, orientation=180,
            signal_subtype = signal_sub_type.three_aspect,
            sig_callback=sig_callback, sig_passed_button = True,
            rhfeather45= True, position_light=True,
            refresh_immediately = False)

    create_colour_light_signal(canvas,11,1500,600, orientation=180,
            signal_subtype = signal_sub_type.four_aspect,
            sig_callback=sig_callback, sig_passed_button = True,
            lhfeather45=True, rhfeather45=True, rhfeather90=True,
            refresh_immediately = False)
    
    create_colour_light_signal (canvas,12,750,600, orientation=180,
            signal_subtype = signal_sub_type.four_aspect,
            sig_callback=sig_callback, sig_passed_button = True,
            refresh_immediately = False)

    create_colour_light_signal (canvas,13,750,650, orientation=180,
            signal_subtype = signal_sub_type.four_aspect,
            sig_callback=sig_callback, sig_passed_button = True,
            refresh_immediately = False)

    create_ground_position_signal(canvas,14,550,250, shunt_ahead=True,
            sig_callback=sig_callback)

    create_ground_position_signal(canvas,15,575,400,
            sig_callback=sig_callback)

    create_ground_position_signal(canvas,16,1300,400,orientation=180,
            shunt_ahead=True, sig_callback=sig_callback,)

    create_colour_light_signal (canvas,20,1850,600, orientation=180,
            signal_subtype = signal_sub_type.four_aspect,
            sig_callback=sig_callback,sig_passed_button=True,fully_automatic=True,
            refresh_immediately = False)
    
    create_colour_light_signal (canvas,21,100,600, orientation=180,
            signal_subtype = signal_sub_type.four_aspect,
            sig_callback=sig_callback,fully_automatic=True)
    
    create_colour_light_signal (canvas,22,50,550,
            signal_subtype = signal_sub_type.four_aspect,
            sig_callback=sig_callback,sig_passed_button=True,fully_automatic=True,
            refresh_immediately = False)
    
    create_colour_light_signal (canvas,23,1800,550,
            signal_subtype = signal_sub_type.four_aspect,
            sig_callback=sig_callback,fully_automatic=True)
                            
    return()

#----------------------------------------------------------------------
# Externally called function to colour the track sections according to the
# track power section switches and the point settings (to reflect what
# sections are powered andwhere they are powered from (up, down, branch,
# or local). Called when either a section switch or point has been changed
#----------------------------------------------------------------------

def update_track_schematic(canvas):
    
    # Global baseline colour definition (everything else inherits from these)
    global up_colour, down_colour, branch_colour, local_colour, off_colour

    # Global drawing objects for the main station schematic
    global platform1, platform2, platform3, through_loop, goods_loop
    global lh_headshunt, lh_auto_sec1, lh_auto_sec2, lh_auto_sec3
    global rh_headshunt, rh_auto_sec1, rh_auto_sec2, rh_auto_sec3
    
    # Global drawing objects for the Goods Yard Schematic
    global goods_yard, point10, point12, point13, point14, point15, point16, point17
    global siding1, siding2, siding3, siding4, siding5, siding6, siding7, siding8

    # Global drawing objects for the MPD Schematic
    global mpd, point20, point21, point22, point23, mpd1, mpd2, mpd3, mpd4, mpd5, mpd6

    #-----------------------------------------------------------------------------------------------
    # Do the headshunts, mpd and goods yard first (as other sections can "inherit" from them)
    #-----------------------------------------------------------------------------------------------
    
    # lh Headshunt
    if power_switches.switch_active(6,1): lh_headshunt_colour = branch_colour 
    elif power_switches.switch_active(6,2): lh_headshunt_colour = local_colour
    else: lh_headshunt_colour = off_colour
    for i in lh_headshunt: canvas.itemconfig (i, fill=lh_headshunt_colour)
    
    # rh Headshunt
    if power_switches.switch_active(7,1): rh_headshunt_colour = branch_colour 
    elif power_switches.switch_active(7,2): rh_headshunt_colour = local_colour
    else: rh_headshunt_colour = off_colour
    for i in rh_headshunt: canvas.itemconfig (i, fill=rh_headshunt_colour)
    
    # goods yard and headshunt
    if power_switches.switch_active(8,1): goods_yard_colour = local_colour 
    else: goods_yard_colour = off_colour
    for i in goods_yard: canvas.itemconfig (i, fill=goods_yard_colour)

    # Motive Power Depot
    if power_switches.switch_active(9,1): mpd_colour = local_colour 
    else: mpd_colour = off_colour
    for i in mpd: canvas.itemconfig (i, fill=mpd_colour)

    #-----------------------------------------------------------------------------------------------
    # Work through the auto sections in the appropriate sequence of inheritence
    # (i.e. some auto sections will inherit from other auto sections)
    #-----------------------------------------------------------------------------------------------

    if point_switched(1): lh_auto_sec1_colour = down_colour
    else: lh_auto_sec1_colour = up_colour
    for i in lh_auto_sec1: canvas.itemconfig (i, fill=lh_auto_sec1_colour)

    if point_switched(2): lh_auto_sec2_colour = lh_auto_sec1_colour
    else: lh_auto_sec2_colour = lh_headshunt_colour
    for i in lh_auto_sec2:canvas.itemconfig(i, fill=lh_auto_sec2_colour)
    
    if point_switched(4): lh_auto_sec3_colour = lh_auto_sec2_colour
    else: lh_auto_sec3_colour = mpd_colour
    # We colour this in later with the goods loop
    
    if point_switched(9): rh_auto_sec1_colour = down_colour
    else: rh_auto_sec1_colour = up_colour
    for i in rh_auto_sec1: canvas.itemconfig (i,fill=rh_auto_sec1_colour)

    if point_switched(8): rh_auto_sec2_colour = rh_auto_sec1_colour
    else: rh_auto_sec2_colour = rh_headshunt_colour
    for i in rh_auto_sec2: canvas.itemconfig (i, fill=rh_auto_sec2_colour)
    
    if point_switched(6): rh_auto_sec3_colour = rh_auto_sec2_colour
    else: rh_auto_sec3_colour = goods_yard_colour
    # We colour this in later with the goods loop
    
    #-----------------------------------------------------------------------------------------------
    # Switch the remaining platform and loop sections (that may depend on the auto sections)
    #-----------------------------------------------------------------------------------------------

    if power_switches.switch_active(1,1) and point_switched(5):
        goods_loop_colour = goods_yard_colour
        lh_auto_sec3_colour = off_colour
        rh_auto_sec3_colour = goods_loop_colour
    elif power_switches.switch_active(1,1) and not point_switched(5):
        goods_loop_colour = lh_auto_sec3_colour
        rh_auto_sec3_colour = goods_loop_colour
    elif power_switches.switch_active(1,2):
        goods_loop_colour = rh_auto_sec3_colour
        lh_auto_sec3_colour = goods_loop_colour
    else:
        goods_loop_colour = off_colour
        rh_auto_sec3_colour = off_colour
        lh_auto_sec3_colour = off_colour

    for i in goods_loop: canvas.itemconfig (i, fill=goods_loop_colour)
    for i in rh_auto_sec3: canvas.itemconfig (i, fill=rh_auto_sec3_colour)
    for i in lh_auto_sec3: canvas.itemconfig (i, fill=lh_auto_sec3_colour)

    if power_switches.switch_active(2,1):
        for i in platform3: canvas.itemconfig(i,fill = lh_auto_sec2_colour)
    elif power_switches.switch_active(2,2):
        for i in platform3: canvas.itemconfig(i,fill = rh_auto_sec2_colour)
    else:
        for i in platform3: canvas.itemconfig(i,fill = off_colour)

    if power_switches.switch_active(3,1):
        for i in platform2: canvas.itemconfig (i, fill = up_colour)
    else:
        for i in platform2: canvas.itemconfig (i, fill = off_colour)

    if power_switches.switch_active(4,1):
        for i in through_loop: canvas.itemconfig (i, fill = down_colour)
    else:
        for i in through_loop: canvas.itemconfig (i, fill = off_colour)

    if power_switches.switch_active(5,1):
        for i in platform1: canvas.itemconfig (i, fill = down_colour)
    else:
        for i in platform1: canvas.itemconfig (i, fill = off_colour)
    
    #-----------------------------------------------------------------------------------------------
    # Change the colours of the the goods yard sections according to the point settings
    # (Track power is switched by the point settings - fed from the LH Headshunt
    #-----------------------------------------------------------------------------------------------

    # The easiest thing to do is to switch off everything and then only switch on what we need
    all_sidings = (point10 + point12 + point13 + point14 + point15 + point16 + point17 +
            siding1 + siding2 + siding3 + siding4 + siding5 + siding6 + siding7 + siding8)
    for i in all_sidings: canvas.itemconfig (i, fill = off_colour)

    if point_switched(18):
        for i in siding1: canvas.itemconfig (i, fill = goods_yard_colour)  
    else :
        for i in point14: canvas.itemconfig (i, fill = goods_yard_colour)
        if point_switched(14):
            for i in point15: canvas.itemconfig (i, fill = goods_yard_colour)
            if point_switched(15):
                for i in point16: canvas.itemconfig (i, fill = goods_yard_colour)
                if point_switched(16):
                    for i in point17: canvas.itemconfig (i, fill = goods_yard_colour)
                    
                    if point_switched(17):
                        for i in siding2: canvas.itemconfig (i, fill = goods_yard_colour)
                    else:
                        for i in siding3: canvas.itemconfig (i, fill = goods_yard_colour)
                else: #point16 not switched
                    for i in siding4: canvas.itemconfig (i, fill = goods_yard_colour)  
            else: #point15 not switched
                for i in siding5: canvas.itemconfig (i, fill = goods_yard_colour)
        else: #point14 not switched
            for i in point13: canvas.itemconfig (i, fill = goods_yard_colour)
            if point_switched(13):
                for i in point12: canvas.itemconfig (i, fill = goods_yard_colour)
                if point_switched(12):
                    for i in point10: canvas.itemconfig (i, fill = goods_yard_colour)
                    if not point_switched(10):
                        for i in siding8: canvas.itemconfig (i, fill = goods_yard_colour)
                else: #point12  not switched
                    for i in siding7: canvas.itemconfig (i, fill = goods_yard_colour)
            else: #point13 not switched
                for i in siding6: canvas.itemconfig (i, fill = goods_yard_colour)
 
    #-----------------------------------------------------------------------------------------------
    # Change the colours of the the MPD sections according to the point settings
    # (Track power is switched by the point settings - if MPD section switch is active)
    #-----------------------------------------------------------------------------------------------

    # The easiest thing to do is to switch off everything and then only switch on what we need
    all_sidings = point20 + point21 + point22 + point23 + mpd1 + mpd2 + mpd3 +mpd4 + mpd5 + mpd6
    for i in all_sidings: canvas.itemconfig (i, fill = off_colour)

    if point_switched(19):
        for i in mpd1: canvas.itemconfig (i, fill = mpd_colour)  
    else:
        for i in point20: canvas.itemconfig (i, fill = mpd_colour)
        
        if point_switched(20):
            for i in point22: canvas.itemconfig (i, fill = mpd_colour)
            
            if point_switched(22):
                for i in mpd2: canvas.itemconfig (i, fill = mpd_colour)
                
            else: # point 22 not switched
                for i in point23: canvas.itemconfig (i, fill = mpd_colour)
                if point_switched(23):
                    for i in mpd3: canvas.itemconfig (i, fill = mpd_colour)
                else: # point 23 not switched
                    for i in mpd4: canvas.itemconfig (i, fill = mpd_colour)
                    
        else: # point 20 not switched
            for i in point21: canvas.itemconfig (i, fill = mpd_colour)
            if point_switched(21):
                for i in mpd5: canvas.itemconfig (i, fill = mpd_colour)
            else: # point 21 not switched
                for i in mpd6: canvas.itemconfig (i, fill = mpd_colour)

            
    return()


