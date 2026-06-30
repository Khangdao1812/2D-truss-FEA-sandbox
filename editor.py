import pygame as pg
import math
from visualization import transform_coordinate, convert_screen_to_world,snap_quarter
import numpy as np



def pick_closest_node(node_screen_position, mouse_pos,cam_object) : #on screen
    picked_node = []
    for key in node_screen_position : 
        x,y = node_screen_position[key]
        dx = abs(mouse_pos[0]-x)
        dy = abs(mouse_pos[1]-y)
        distance_of_detection = round(5*cam_object.zoom_factor)
        if dx<distance_of_detection and dy<distance_of_detection : 
            picked_node.append(key)
    if len(picked_node) == 0 : return None
    else : 
        return picked_node[0]




class Editor : 
    def __init__(self, input_force,node_list,free_node_list,connections) : 
        self.moving_vector = False
        self.selecting_node = None
        self.input_force = input_force.copy()
        self.force_vector_list = []
        self.vector_to_force = 3e6
        self.position_dictionary_editor = {}
        self.selecting_vector = None
        self.structure_editor = False
        self.creating_bars = False
        self.selecting_node_N = None
        self.selecting_bar_N = None
        self.node_list = node_list.copy()
        self.free_node_list = free_node_list.copy()
        self.connections = connections.copy()

        self.editing_bar_property = None      # "A" hoặc "E"
        self.input_text = ""

    def detect_key_force_editor(self,event,cam_object) : 
        self.last_mouse = pg.mouse.get_pos() 
        if event.type == pg.MOUSEBUTTONDOWN : 
            if event.button ==3 : 
                if self.moving_vector : 
                    self.moving_vector = False
                    self.last_mouse = None

                else : 
                    self.selecting_node = pick_closest_node(self.position_dictionary_editor,self.last_mouse, cam_object)
                    if self.selecting_node is not None :
                        self.moving_vector = True
                        if self.selecting_vector is not None : 
                            self.selecting_vector.selected = False
                            self.selecting_vector = None


            elif event.button == 1 : 
                if self.moving_vector : 
                    self.moving_vector = False
                    node = self.node_list[self.selecting_node]
                    mouse = convert_screen_to_world(*self.last_mouse,cam_object)

                    vector = Force_vector(self.selecting_node,*node,*mouse, self.vector_to_force)
                    vector.add_force(self.input_force)
                    self.force_vector_list.append(vector)
                    vector.update_position_on_screen(cam_object)
                else : 
                    for vector in self.force_vector_list :
                        if vector.detect_selection(*self.last_mouse) : 
                            vector.selected = True

                            if self.selecting_vector is not None : 
                                self.selecting_vector.selected = False
                            self.selecting_vector = vector
                            return None
                    if self.selecting_vector is not None : 
                        self.selecting_vector.selected = False
                        self.selecting_vector = None

        elif event.type == pg.KEYDOWN : #####

            if event.key == pg.K_BACKSPACE : 
                if self.selecting_vector is not None : 
                    self.selecting_vector.selected = False
                    self.selecting_vector.remove_force(self.input_force)
                    self.force_vector_list.remove(self.selecting_vector)
                    self.selecting_vector = None

    def draw_mouse_vector(self,screen_var, node_positions_screen,zoom_factor) : #sau detect mousse
        if self.moving_vector : 
            Force_vector.draw_force_vector(screen_var, 'yellow', node_positions_screen[self.selecting_node],self.last_mouse, round(3*zoom_factor))

    def update_vector_screen_position(self,cam) : 
        for vectors in self.force_vector_list : 
            vectors.update_position_on_screen(cam)
    
    def intepret_force_array(self, world_node_list) : 
        i=0
        while 2*i+1 < len(self.input_force) : 
            horizontal, vertical = self.input_force[2*i], self.input_force[2*i+1] 
            if horizontal != 0 or vertical != 0 : 
                start_x = world_node_list[i][0]
                start_y = world_node_list[i][1]
                end_x = horizontal/self.vector_to_force + start_x
                end_y = vertical/self.vector_to_force + start_y
                new_vector = Force_vector(i, start_x, start_y, end_x,end_y, self.vector_to_force)
                self.force_vector_list.append(new_vector)
            i += 1


    def find_selected_bar(self, mouse_pos,cam):
        click_tolerance = 5*cam.zoom_factor  # pixel
        selected_bar = None
        best_distance_sq = click_tolerance ** 2

        px, py = mouse_pos

        for bar_index, bar in enumerate(self.connections):

            node_a_idx = bar[0]
            node_b_idx = bar[1]

            ax, ay = self.position_dictionary_editor[node_a_idx]
            bx, by = self.position_dictionary_editor[node_b_idx]

            dx = bx - ax
            dy = by - ay

            length_sq = dx * dx + dy * dy
            if length_sq == 0:
                continue

            t = ((px - ax) * dx + (py - ay) * dy) / length_sq

            t = max(0.0, min(1.0, t))
            qx = ax + t * dx
            qy = ay + t * dy

            dist_sq = (px - qx) ** 2 + (py - qy) ** 2

            if dist_sq < best_distance_sq:
                best_distance_sq = dist_sq
                selected_bar = bar_index

        return selected_bar

    def detect_key_edit_structure(self,event,structure, cam) : 
        self.last_mouse = pg.mouse.get_pos() 
        if event.type == pg.MOUSEBUTTONDOWN : 
            if event.button == 2: 
                if self.creating_bars == False : 
                    mouse_world_pos = convert_screen_to_world(*self.last_mouse,cam)
                    closest_world_lattice = (snap_quarter(mouse_world_pos[0]),snap_quarter(mouse_world_pos[1]))
                    closest_screen_lattice = transform_coordinate(cam.screen_x, cam.screen_y,cam.scale, 
                                                                *closest_world_lattice, cam)
                    distance_on_screen = (self.last_mouse[0]-closest_screen_lattice[0])**2 + (self.last_mouse[1]-closest_screen_lattice[1])**2
                    if distance_on_screen<10**2 : 
                        if closest_world_lattice in self.node_list and closest_world_lattice in self.free_node_list: 
                            self.free_node_list.remove(closest_world_lattice)
                        elif closest_world_lattice in self.node_list and closest_world_lattice not in self.free_node_list : 
                            self.free_node_list.append(closest_world_lattice)
                        else : 
                            self.node_list.append(closest_world_lattice)
                            self.free_node_list.append(closest_world_lattice)
                            self.position_dictionary_editor[len(self.node_list)-1]= closest_screen_lattice
                            self.input_force = np.append(self.input_force,[0,0])
                
            if event.button == 1 :
                if self.creating_bars == True : 
                    ending_node = pick_closest_node(self.position_dictionary_editor,self.last_mouse, cam)
                    if ending_node != None : 
                        #######DEFAULT VALUES
                        self.connections.append((min(self.begin_node,ending_node), max(self.begin_node,ending_node), 1e-2, 200e9, 4e8,4e8))
                        structure.model_stress.append(0.0) ###
                        structure.model_colour.append((76, 136, 255))####

                        self.creating_bars = False
                        self.begin_node = None
                    else : 
                        self.begin_node = None
                        self.creating_bars = False
                
                else : 
                    self.selecting_node_N = pick_closest_node(self.position_dictionary_editor,self.last_mouse, cam) #index
                    if self.selecting_node_N is not None : 
                        self.selecting_bar_N = None
                    else : 
                        self.selecting_bar_N = self.find_selected_bar(self.last_mouse,cam) #index

            if event.button == 3 : 
                if self.creating_bars == False : 
                    self.begin_node = pick_closest_node(self.position_dictionary_editor,self.last_mouse, cam)
                    if self.begin_node != None : 
                        self.creating_bars = True
                else : 
                    self.creating_bars = False
                    self.begin_node = None

        elif event.type == pg.KEYDOWN : 
            if self.editing_bar_property is None:
                if self.selecting_bar_N is not None:
                    if event.key == pg.K_a:
                        self.editing_bar_property = "A"
                        self.input_text = ""
                        return
                    elif event.key == pg.K_e:
                        self.editing_bar_property = "E"
                        self.input_text = ""
                        return
            
            if self.editing_bar_property is not None:
                if event.key == pg.K_ESCAPE:
                    self.editing_bar_property = None
                    self.input_text = ""
                    return
                elif event.key == pg.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                    return
                elif event.key == pg.K_RETURN:
                    try:
                        value = float(self.input_text)
                        a,b,A,E,UTS,UCS = self.connections[self.selecting_bar_N]
                        if self.editing_bar_property == "A":
                            A = value
                        else:
                            E = value
                        self.connections[self.selecting_bar_N] = (a,b,A,E,UTS,UCS)
                    except:
                        pass
                    self.editing_bar_property = None
                    self.input_text = ""
                    return
                elif event.unicode in "0123456789.eE-":
                    self.input_text += event.unicode
                    return

            if event.key == pg.K_BACKSPACE : 
                if self.selecting_bar_N is not None : 
                    self.connections.pop(self.selecting_bar_N)
                    structure.model_stress.pop(self.selecting_bar_N) ###
                    structure.model_colour.pop(self.selecting_bar_N) ####
                    self.selecting_bar_N = None

                elif self.selecting_node_N is not None : 
                    node_name = self.node_list[self.selecting_node_N]
                    self.node_list.pop(self.selecting_node_N)
                    if node_name in self.free_node_list : 
                        self.free_node_list.remove(node_name)

                    # position dictionary
                    del self.position_dictionary_editor[self.selecting_node_N]
                    for key in sorted(list(self.position_dictionary_editor.keys())):
                        if key > self.selecting_node_N:
                            self.position_dictionary_editor[key - 1] = self.position_dictionary_editor[key]
                            del self.position_dictionary_editor[key]

                    # force vector
                    self.input_force = np.delete(self.input_force,[2 * self.selecting_node_N, 2 * self.selecting_node_N + 1])

                    # force arrows
                    for i in range(len(self.force_vector_list) - 1, -1, -1):

                        vector = self.force_vector_list[i]

                        if vector.from_node == self.selecting_node_N:
                            self.force_vector_list.pop(i)

                        elif vector.from_node > self.selecting_node_N:
                            vector.from_node -= 1
                            vector.start_x = self.node_list[vector.from_node][0]
                            vector.start_y = self.node_list[vector.from_node][1]

                    # members
                    for i in range(len(self.connections) - 1, -1, -1):
                        member = self.connections[i]

                        if member[0] == self.selecting_node_N or member[1] == self.selecting_node_N:

                            self.connections.pop(i)
                            structure.model_stress.pop(i) ###
                            structure.model_colour.pop(i) ####

                        else:
                            a, b, c, d, e, f = member
                            if a > self.selecting_node_N:
                                a -= 1
                            if b > self.selecting_node_N:
                                b -= 1

                            self.connections[i] = (a, b, c, d, e,f)
                    self.selecting_node_N = None




class Force_vector : 
    def __init__(self,from_node,start_x,start_y,end_x, end_y,coordinate_magnitude_scale) : #these positions are in the real world
        self.start_x , self.start_y = start_x, start_y
        self.end_x, self.end_y = end_x, end_y
        self.x_component= (end_x-start_x)*coordinate_magnitude_scale
        self.y_component = (end_y-start_y)*coordinate_magnitude_scale
        self.magnitude = math.sqrt(self.x_component**2+self.y_component**2)
        self.from_node = from_node #=selected node
        self.selected = False
        self.angle = math.atan2(self.x_component, self.y_component)
        self.text_angle = -math.degrees(self.angle)+90
        if self.text_angle >90 and self.text_angle <270 : 
            self.text_angle += 180

    @staticmethod
    def draw_force_vector(screen, color, start, end, line_thickness):
        pg.draw.line(screen, color, start, end, line_thickness)
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        angle = math.atan2(dy, dx)
        arrow_size = 10
        x1 = end[0] - arrow_size * math.cos(angle - math.pi/6)
        y1 = end[1] - arrow_size * math.sin(angle - math.pi/6)
        x2 = end[0] - arrow_size * math.cos(angle + math.pi/6)
        y2 = end[1] - arrow_size * math.sin(angle + math.pi/6)
        pg.draw.line(screen, color, end, (x1, y1), line_thickness)
        pg.draw.line(screen, color, end, (x2, y2), line_thickness)

    def add_force(self,input_force) : 
        input_force[2*self.from_node] += self.x_component
        input_force[2*self.from_node +1] += self.y_component

    def remove_force(self,input_force) : 
        input_force[2*self.from_node] -= self.x_component
        input_force[2*self.from_node+1] -= self.y_component

    def update_position_on_screen(self,cam) : 
        self.start_position = transform_coordinate(cam.screen_x, cam.screen_y, cam.scale, self.start_x,self.start_y, cam)
        self.end_position = transform_coordinate(cam.screen_x, cam.screen_y, cam.scale, self.end_x,self.end_y, cam) #world- > screen

    def detect_selection(self, mouse_x, mouse_y) : 
        self.basis_vector_x = self.end_position[0]-self.start_position[0]
        self.basis_vector_y = self.end_position[1]-self.start_position[1]
        basis_vector_length = self.basis_vector_x**2+self.basis_vector_y**2
        t = ((self.basis_vector_x*(mouse_x-self.start_position[0])+self.basis_vector_y*(mouse_y-self.start_position[1])))/(self.basis_vector_x**2+self.basis_vector_y**2)
        if 0<=t<=1 : 
            distance_to_start_point = (mouse_x-self.start_position[0])**2 + (mouse_y-self.start_position[1])**2
            start_point_to_intersection = basis_vector_length*t*t
            distance_to_line = distance_to_start_point - start_point_to_intersection #all of the distances & lengths are squared
            if distance_to_line < 10**2 : #5 pixels
                return self
        return False

    def render_fixed_vector(self,screen_variable,cam) : #this function is in main 
       
        colour = ('yellow' if self.selected == False else 'green')
        self.draw_force_vector(
            screen_variable,
            colour,
            self.start_position,
            self.end_position,
            round(3*cam.zoom_factor)
        )

        dx,dy = math.cos(self.angle), math.sin(self.angle)

        mx = (self.start_position[0] + self.end_position[0]) / 2
        my = (self.start_position[1] + self.end_position[1]) / 2
        tx,ty = mx+35*dy*cam.zoom_factor, my+35*-dx*cam.zoom_factor

        label = f"{self.magnitude / 1000:.1f} kN"
        font = pg.font.SysFont(None, round(25 * cam.zoom_factor))
        text = font.render(label, True, pg.Color("white"))

        rotated_text = pg.transform.rotate(text, self.text_angle)

        text_rect = rotated_text.get_rect(center=(tx, ty))

        # background
       
        padding_x = 10
        padding_y = 6

        bg_rect = text_rect.inflate(padding_x, padding_y)

        bg_surface = pg.Surface((bg_rect.width, bg_rect.height), pg.SRCALPHA)

        pg.draw.rect(bg_surface,(0, 0, 0, 160),bg_surface.get_rect(),border_radius=6)

        pg.draw.rect(bg_surface,(255, 255, 255, 40),bg_surface.get_rect(),width=1,border_radius=6)

        screen_variable.blit(bg_surface, bg_rect.topleft)

        screen_variable.blit(rotated_text, text_rect)

#technical detail : for safety, if moving_vector = False I deliberately force the mouse vector ouput in main = None
# In reality, if moving_vector is False, we dont even care about the mouse vector
## This double layer verification makes it easy to generalize in case of scrolling as in line #47, where I am quite lazy to
#rewrite the whole logic as case no mouse button clicked. Actually at the lines 48-51, I can just do return both (node_screen_position[selecting_node],last_mouse) ,moving_vector
# and I'd still be fine. But the problem is, if selecting node is None -> key error so I guess I'll have to copy the logic
# as lines for case no mouse button clicked

#force_array,drawing vector, draw_moving_vector,  moving_vector

#force vector to draw list, modified force array, selected node, moving arrows or not?


#{0: (364.0, 657.0), 1: (414.0, 657.0), 2: (464.0, 657.0)}
