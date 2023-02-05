from system_test_harness import *
import copy

# ------------------------------------------------------------------------------
# Functions to excersise the schematic Editor - Create Functions
# ------------------------------------------------------------------------------

def create_line():
    objects.create_object(objects.object_type.line)
    object_id = list(objects.schematic_objects)[-1]
    return(object_id)
    
def create_colour_light_signal():
    objects.create_object(objects.object_type.signal,
                        signals_common.sig_type.colour_light.value,
                        signals_colour_lights.signal_sub_type.four_aspect.value)
    object_id = list(objects.schematic_objects)[-1]
    return(object_id)

def create_semaphore_signal():
    objects.create_object(objects.object_type.signal,
                           signals_common.sig_type.semaphore.value,
                           signals_semaphores.semaphore_sub_type.home.value)
    object_id = list(objects.schematic_objects)[-1]
    return(object_id)

def create_ground_position_signal():
    objects.create_object(objects.object_type.signal,
                           signals_common.sig_type.ground_position.value,
                           signals_ground_position.ground_pos_sub_type.standard.value)
    object_id = list(objects.schematic_objects)[-1]
    return(object_id)

def create_ground_disc_signal():
    objects.create_object(objects.object_type.signal,
                           signals_common.sig_type.ground_disc.value,
                           signals_ground_disc.ground_disc_sub_type.standard.value)
    object_id = list(objects.schematic_objects)[-1]
    return(object_id)

def create_track_section():
    objects.create_object(objects.object_type.section)
    object_id = list(objects.schematic_objects)[-1]
    return(object_id)

def create_block_instrument():
    objects.create_object(objects.object_type.instrument)
    object_id = list(objects.schematic_objects)[-1]
    return(object_id)

def create_left_hand_point():
    objects.create_object(objects.object_type.point,points.point_type.LH.value)
    object_id = list(objects.schematic_objects)[-1]
    return(object_id)

def create_right_hand_point():
    objects.create_object(objects.object_type.point,points.point_type.LH.value)
    object_id = list(objects.schematic_objects)[-1]
    return(object_id)

# ------------------------------------------------------------------------------
# Functions to excersise the schematic Editor - Move and update
# ------------------------------------------------------------------------------

def get_object_position (object_id):
    xpos = objects.schematic_objects[object_id]["posx"] + 10
    ypos = objects.schematic_objects[object_id]["posy"]
    return(xpos, ypos)

def update_object(object_id, new_values:dict):
    if object_id not in objects.schematic_objects.keys():
        raise_test_warning ("update_object - object:"+str(object_id)+" does not exist")
    else:
        new_object = copy.deepcopy(objects.schematic_objects[object_id])        
        for element in new_values.keys():
            if element not in new_object.keys():
                raise_test_warning ("update_object - element:"+element+" is not valid")
            else:
                new_object[element] = new_values[element]
        objects.update_object(object_id, new_object)                
        sleep(0.001)

def select_or_deselect_objects(*object_ids):
    for object_id in object_ids:
        xpos, ypos = get_object_position(object_id)
        schematic.canvas.event_generate("<Shift-Button-1>", x=xpos, y=ypos)
        sleep(0.001)
        schematic.canvas.event_generate("<ButtonRelease-1>")
        sleep(0.001)
        
def select_single_object(object_id):
    xpos, ypos = get_object_position(object_id)
    schematic.canvas.event_generate("<Button-1>", x=xpos, y=ypos)
    sleep(0.001)
    schematic.canvas.event_generate("<ButtonRelease-1>")
    sleep(0.001)
    
def select_and_move_objects(object_id,xdiff:int, ydiff:int, steps:int=100, time:int=2):
    startx, starty = get_object_position(object_id)
    schematic.canvas.event_generate("<Button-1>", x=startx, y=starty)
    sleep(0.001)
    sleep_time = time/steps
    for step in range(steps):
        cursorx = startx+step*(xdiff/steps)
        cursory = starty+step*(ydiff/steps)
        schematic.canvas.event_generate("<Motion>", x=cursorx, y=cursory)
        sleep(sleep_time)
    schematic.canvas.event_generate("<ButtonRelease-1>")
    sleep(0.001)
    
def rotate_selected_objects(object_id):
    schematic.canvas.event_generate("<r>")
    sleep(0.001)

def delete_selected_objects(object_id):
    schematic.canvas.event_generate("<Delete>")
    sleep(0.001)
    
def deselect_all_objects(object_id):
    schematic.canvas.event_generate("<Escape>")
    sleep(0.001)
    
def copy_selected_objects(object_id):
    schematic.canvas.event_generate("<Control-Key-c>")
    sleep(0.001)
    
def paste_copied_objects(object_id):
    schematic.canvas.event_generate("<Control-Key-v>")

#################################################################################################
    
        
initialise_test_harness()
s1 = create_colour_light_signal()
update_object(s1, {"itemid":10})
s2 = create_colour_light_signal()
s3 = create_colour_light_signal()
select_or_deselect_objects (s1,s3)
select_single_object(s2)
p1 = create_left_hand_point()
p2 = create_right_hand_point()
select_or_deselect_objects(s1,p1)
select_and_move_objects(s1,590,190)
complete_tests(shutdown=False)


    
