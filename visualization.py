import pygame as pg

def transform_coordinate(scrx,scry,scale,x_input, y_input,camera_object) : #The origin will be at the middle of the base. So  (0,0) -> (screenx/2,screeny)
    return ((x_input*scale*camera_object.zoom + scrx//2)-camera_object.camx, (scry-y_input*scale*camera_object.zoom)-camera_object.camy) #this is world coordinate.
    #world->screen

def convert_screen_to_world(x,y,cam) :  #opposite of visualization's transform coordinate
    return ((x + cam.camx - cam.screen_x//2)/(cam.zoom*cam.scale),(y+cam.camy-cam.screen_y)/(-cam.zoom*cam.scale))
    #screen->world

def node_position_list(sx,sy,sc,nodes,camera_object) : #ran out of names
    node_dictionary = {}
    for i in range(0,len(nodes)) : 
        node_dictionary[i] = transform_coordinate(sx,sy,sc,*nodes[i],camera_object)
    return node_dictionary

def hsv_to_rgb(h, s, v): #formula is available online
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return (r + m, g + m, b + m)

def bar_colour(structure_object) : 
    # stress or strain / cross section area -> compare with ultimate strength. For steel, stress is approximately equal to strain.
    if structure_object.viewing_mode == 0 : viewing_mode = 'stress utilization heatmap'
    elif structure_object.viewing_mode == 1 : viewing_mode = 'force heatmap'

    if viewing_mode == 'stress utilization heatmap' : 
        colour = []
        for i in range(0, len(structure_object.now_stress)) : 
            stress = structure_object.now_stress[i]
            member = structure_object.now_truss[i]
            if stress >= 0 : 
                r = abs(stress/member[4]) #UTS
            else : 
                r = max(abs(stress/member[5]),abs(stress*member[2]/structure_object.critical_buckling_load[i])) #UCS
            if r >1.5 : r = 1.5
            t = r**2 #non-linear mapping
            if r <= 1.0:
                    # xanh (220) → đỏ (0)
                    h = 220 * (1 - t)
                    # saturation tăng dần
                    s = 0.7 + 0.3 * t
                    # giữ sáng
                    v = 1.0

            else:
                # fail → tím
                h = 280
                s = 1.0
                # fade out
                beta = 1.5
                v = max(0.3, 1.0 - beta * (r - 1.0))
            rgb = hsv_to_rgb(h,s,v)
            true_rgb = tuple(int(c * 255) for c in rgb)
            colour.append(true_rgb)


    elif viewing_mode == 'force heatmap' : 
        return structure_object.force_heat_map_colour
    return colour

def calculate_force_heatmap(axial_forces) :
    colour = []
    max_force = max(abs(f) for f in axial_forces if f is not None)

    for force in axial_forces:
        if max_force > 1e-3 : 
            r = force / max_force
            # tăng độ tương phản
            t = abs(r) ** 0.7

            if r >= 0:
                # trắng -> đỏ
                h = 0
                s = t
                v = 1.0

            else:
                # trắng -> xanh
                h = 220
                s = t
                v = 1.0

            rgb = hsv_to_rgb(h, s, v)
            true_rgb = tuple(int(c * 255) for c in rgb)
            colour.append(true_rgb)
        else : 
            colour.append((1,1,1))
    return colour


def line_clip(p1,p2) : 

    screen_box = pg.Rect(0,0,800,600)
    clipped_line = screen_box.clipline(p1,p2)
    if clipped_line : 
        return clipped_line
    else : 
        return False

def draw_structure(scr,dict,nodes,freenodes, connect,colour,cam,editor) : 
    count = 0 
    for individual_connections in connect:
        line = line_clip(dict[individual_connections[0]],dict[individual_connections[1]])

        if line == False : 
            count+=1
            continue
        else : 
            pg.draw.line(scr,('green' if editor.selecting_bar_N == count else colour[count]),
                        tuple(map(int, line[0])), tuple(map(int, line[1])), round(4*cam.zoom_factor)) 
    #Lỗi list index của colour[count] out of range khi simulation để đến collapsed, sau đó quay qua editor xóa một thanh
    #rồi quay trở lại simulation. Lỗi do đã update connections và model colors nhưng khi collapse cái prev truss nó ko được
    #update nên nó dài hơn cái color -> index out of range.
        count += 1

        
    count =0
    for individual_node in dict : 
        if editor.selecting_node_N == count : 
            color = 'green'
        else : 
            if nodes[individual_node] in freenodes : 
                color = 'red' 
            else : 
                color = (80,80,80)
        pg.draw.circle(scr,color,dict[individual_node],round(5*cam.zoom_factor), width = 0) 
        #pygame.draw.circle(surface, color, center, radius, width=0)
        count+=1
  
        
def snap_quarter(x) : 
    return round(4*x)/4

def generate_grid_lines(camera) : 
    generated_line_list = [] #(start, end, colour, stroke size)
    furthest_up_left = convert_screen_to_world(0,0,camera)
    step_on_screen = 0.25*camera.zoom*camera.scale
    start_x_world,start_y_world = snap_quarter(furthest_up_left[0]), snap_quarter(furthest_up_left[1])
    start_on_screen = transform_coordinate(camera.screen_x,camera.screen_y,camera.scale,start_x_world, start_y_world,camera)
    x,y = start_on_screen[0], start_on_screen[1]
    colour = (60, 60, 60)

    while x <= camera.screen_x : 
        if start_x_world.is_integer() : 
            generated_line_list.append(((x,0),(x,camera.screen_y), colour, 2))
        elif (2*start_x_world).is_integer() and camera.zoom> 0.7: 
            if camera.zoom> 2 : 
                stroke_size = 2
            else : 
                stroke_size =1
            generated_line_list.append(((x,0),(x,camera.screen_y), colour, stroke_size))
        elif (4*start_x_world).is_integer() and camera.zoom> 2: 
            generated_line_list.append(((x,0),(x,camera.screen_y), colour, 1))
        x+= step_on_screen
        start_x_world += 0.25

    while y <= camera.screen_y : 
        if start_y_world.is_integer() : 
            generated_line_list.append(((0,y),(camera.screen_x,y), colour, 2))
        elif (2*start_y_world).is_integer()and camera.zoom> 0.7: 
            if camera.zoom> 2 : 
                stroke_size = 2
            else : 
                stroke_size =1
            generated_line_list.append(((0,y),(camera.screen_x,y), colour, stroke_size))
        elif (4*start_y_world).is_integer() and camera.zoom> 2 : 
            generated_line_list.append(((0,y),(camera.screen_x,y), colour, 1))
        y+= step_on_screen
        start_y_world+=0.25
    return generated_line_list

def draw_grid(screen_variable, grid_input_list) : 
    for line in grid_input_list : 
        pg.draw.line(screen_variable,line[2],line[0],line[1],line[3])

#note for visualization : đã có stress sẵn tương ứng với từng bar trong list.

#[(0,3,A1,E1,4e8),(3,6,A1,E1,4e8),(6,9,A1,E1,4e8),(1,4,A1,E1,4e8),(4,7,A1,E1,4e8),(7,10,A1,E1,4e8)
#(2,5,A1,E1,4e8),(5,8,A1,E1,4e8),(8,11,A1,E1,4e8),(0,1,A1,E1,4e8),(1,2,A1,E1,4e8),(3,4,A1,E1,4e8),(4,5,A1,E1,4e8),(6,7,A1,E1,4e8),(7,8,A1,E1,4e8),(9,10,A1,E1,4e8),(10,11,A1,E1,4e8),(0,4,A1,E1,4e8),(4,2,A1,E1,4e8),(3,7,A1,E1,4e8),(7,5,A1,E1,4e8),(6,10,A1,E1,4e8),(10,8,A1,E1,4e8)]
    
#At idle spawning point, px = 300, py = 600
