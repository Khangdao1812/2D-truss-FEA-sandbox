import numpy as np
import pygame as pg
import copy as cp
import math
from solver import solve_truss
from visualization import draw_structure, node_position_list, bar_colour, generate_grid_lines, draw_grid,calculate_force_heatmap
from camera import Camera_class
from editor import Editor
from dataclasses import dataclass, field
import cProfile
import pstats


#############################
A1,E1 = 1e-2,200e9 #m^2, Pa
# ===============================
#nodes_external = [(-1,0),(0,0),(1,0), (-1,2),(0,2),(1,2), (-1,4),(0,4),(1,4), (-1,6),(0,6),(1,6)]
#connections = [(0,3,A1,E1,4e8),(3,6,A1,E1,4e8),(6,9,A1,E1,4e8),(1,4,A1,E1,4e8),(4,7,A1,E1,4e8),(7,10,A1,E1,4e8),(2,5,A1,E1,4e8),(5,8,A1,E1,4e8),(8,11,A1,E1,4e8),(0,1,A1,E1,4e8),(1,2,A1,E1,4e8),(3,4,A1,E1,4e8),(4,5,A1,E1,4e8),(6,7,A1,E1,4e8),(7,8,A1,E1,4e8),(9,10,A1,E1,4e8),(10,11,A1,E1,4e8),(0,4,A1,E1,4e8),(4,2,A1,E1,4e8),(3,7,A1,E1,4e8),(7,5,A1,E1,4e8),(6,10,A1,E1,4e8),(10,8,A1,E1,4e8)]
#free_nodes_external = [(-1,2),(0,2),(1,2), (-1,4),(0,4),(1,4), (-1,6),(0,6),(1,6)]
#F_raw = [(0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (3e7,0), (0,0), (0,0)]

nodes_external = [
    (0, 0), (2, 0), (4, 0), (6, 0), (8, 0),
    (0, 2), (2, 2), (4, 2), (6, 2), (8, 2),
    (0, 4), (2, 4), (4, 4), (6, 4), (8, 4),
    (0, 6), (2, 7), (4, 8), (6, 7), (8, 6)
]

connections = [
    # bottom chord
    (0,1,A1,E1,4e8,4e8),
    (1,2,A1,E1,4e8,4e8),
    (2,3,A1,E1,4e8,4e8),
    (3,4,A1,E1,4e8,4e8),

    # mid lower
    (5,6,A1,E1,4e8,4e8),
    (6,7,A1,E1,4e8,4e8),
    (7,8,A1,E1,4e8,4e8),
    (8,9,A1,E1,4e8,4e8),

    # mid upper
    (10,11,A1,E1,4e8,4e8),
    (11,12,A1,E1,4e8,4e8),
    (12,13,A1,E1,4e8,4e8),
    (13,14,A1,E1,4e8,4e8),

    # roof chord
    (15,16,A1,E1,4e8,4e8),
    (16,17,A1,E1,4e8,4e8),
    (17,18,A1,E1,4e8,4e8),
    (18,19,A1,E1,4e8,4e8),
##########################################
    # verticals
    (0,5,A1,E1,4e8,4e8),
    (1,6,A1,E1,4e8,4e8),
    (2,7,A1,E1,4e8,4e8),
    (3,8,A1,E1,4e8,4e8),
    (4,9,A1,E1,4e8,4e8),

    (5,10,A1,E1,4e8,4e8),
    (6,11,A1,E1,4e8,4e8),
    (7,12,A1,E1,4e8,4e8),
    (8,13,A1,E1,4e8,4e8),
    (9,14,A1,E1,4e8,4e8),

    (10,15,A1,E1,4e8,4e8),
    (11,16,A1,E1,4e8,4e8),
    (12,17,A1,E1,4e8,4e8),
    (13,18,A1,E1,4e8,4e8),
    (14,19,A1,E1,4e8,4e8),

    # diagonals (stability + collapse paths)
    (0,6,A1,E1,4e8,4e8),
    (2,6,A1,E1,4e8,4e8),

    (1,7,A1,E1,4e8,4e8),
    (3,7,A1,E1,4e8,4e8),

    (2,8,A1,E1,4e8,4e8),
    (4,8,A1,E1,4e8,4e8),

    (5,11,A1,E1,4e8,4e8),
    (7,11,A1,E1,4e8,4e8),

    (6,12,A1,E1,4e8,4e8),
    (8,12,A1,E1,4e8,4e8),

    (7,13,A1,E1,4e8,4e8),
    (9,13,A1,E1,4e8,4e8),

    (10,16,A1,E1,4e8,4e8),
    (12,16,A1,E1,4e8,4e8),

    (11,17,A1,E1,4e8,4e8),
    (13,17,A1,E1,4e8,4e8),

    (12,18,A1,E1,4e8,4e8),
    (14,18,A1,E1,4e8,4e8),
]
free_nodes_external = [
    (0, 2), (2, 2), (4, 2), (6, 2), (8, 2),
    (0, 4), (2, 4), (4, 4), (6, 4), (8, 4),
    (0, 6), (2, 7), (4, 8), (6, 7), (8, 6)
]

F_raw = [
    (0, 0), (0, 0), (0, 0), (0, 0), (0, 0),

    (0, 0), (0, 0), (0, 0), (0, 0), (0, 0),

    (0, 0), (0, 0), (0, 0), (0, 0), (0, 0),

    (0, -2e7),   # 15
    (0, -3e7),   # 16
    (0, -4e7),   # 17 (peak roof load)
    (0, -3e7),   # 18
    (0, -2e7)    # 19
]

F = np.array(F_raw)
F = F.flatten()

#=================================


def point_segment_distance(P, A, B):
    """
    P : mouse position
    A,B : two endpoints of bar (screen coordinates)

    return shortest distance from P to segment AB
    """

    px, py = P
    ax, ay = A
    bx, by = B

    abx = bx - ax
    aby = by - ay

    apx = px - ax
    apy = py - ay

    ab2 = abx * abx + aby * aby

    if ab2 == 0:
        return math.hypot(apx, apy)

    t = (apx * abx + apy * aby) / ab2
    t = max(0, min(1, t))

    closest_x = ax + t * abx
    closest_y = ay + t * aby

    return math.hypot(px - closest_x, py - closest_y)

def pick_bar(mouse_pos, structure):

    threshold = 10

    best_bar = None
    best_dist = float("inf")

    for member in structure.structure:

        start = structure.position_dictionary_real[member[0]]
        end   = structure.position_dictionary_real[member[1]]

        d = point_segment_distance(mouse_pos, start, end)

        if d < threshold and d < best_dist:
            best_dist = d
            best_bar = member        

    return best_bar

def remove_failed_member(failed_member,truss,stress,axial_force,P_cr) : 
    truss.pop(failed_member)
    stress.pop(failed_member)
    axial_force.pop(failed_member)
    P_cr.pop(failed_member)

def compute_scale(nodes_input, u):
    nodes_input = np.array(nodes_input) #turns array -> vectors, preserve the structure
    U = u.reshape(len(nodes_input), 2) #reshape into a list length n, 2 columns
    max_disp = np.max(np.linalg.norm(U, axis=1)) #.norm calculates the length of vector, axis =1 means do it for each row [x,y]
    xmin, ymin = nodes_input.min(axis=0) #axis = 0 means working vertically each time, and it also does this for very column.
    xmax, ymax = nodes_input.max(axis=0)
    L = max(xmax - xmin, ymax - ymin)
    world_position = nodes_input + U #vector operation
    node_world_position = [tuple(pos) for pos in world_position]
    return node_world_position, max_disp/L #[tuple(pos) for pos in render_position]

def find_failure(bars,stress_l,axial_force,P_cr_list) : #FAILURE REMOVAL STOPPED  FOR TESTING
    failed_bar = None
    for k in range(len(stress_l)-1,-1,-1) : 
        stress_val = stress_l[k]
        if stress_val >= 0 : 
            if stress_val>1.06*bars[k][4] : 
                #bars.pop(k)
                #stress_l.pop(k)
                #axial_force.pop(k)
                #P_cr_list.pop(k)
                failed_bar = k
        else : 
            if abs(stress_val)>1.06*bars[k][5] : #x1.06 for dark purple color
                #bars.pop(k)
                #stress_l.pop(k)
                #axial_force.pop(k)
                #P_cr_list.pop(k)
                failed_bar = k
            elif abs(stress_val*bars[k][2]) >1.06*P_cr_list[k] : 
                #bars.pop(k)
                #stress_l.pop(k)
                #axial_force.pop(k)
                #P_cr_list.pop(k)
                failed_bar = k
    return failed_bar

def estimate_force_scale(nodes, free_nodes, truss_structure, force_input, euler_buckling_load):
    displacement, reaction, axial_list, stress = solve_truss(nodes, free_nodes, truss_structure, force_input)

    # run force heatmap
    load_heat_map = calculate_force_heatmap(axial_list)

    max_ratio = -float("inf")
    member_with_max_ratio = None
    critical_stress = None

    for i in range(len(stress)):
        stress_val = stress[i]

        if stress_val >= 0:
            sigma_limit = truss_structure[i][4]      # UTS
            ratio = stress_val / sigma_limit

        else:
            sigma_ucs = truss_structure[i][5]        # UCS
            sigma_buckling = (euler_buckling_load[i]/ truss_structure[i][2])           # Pcr / A
            sigma_limit = min(sigma_ucs, sigma_buckling) #thường sigma buckling bé hơn
            ratio = abs(stress_val) / sigma_limit

        if ratio > 1.06 and ratio > max_ratio:
            max_ratio = ratio
            member_with_max_ratio = i
            critical_stress = sigma_limit
    if member_with_max_ratio is not None:
        predicted_force_scale = (critical_stress/abs(stress[member_with_max_ratio]))

        return max(0.003,predicted_force_scale), load_heat_map, axial_list, stress

    return 1.0, load_heat_map, axial_list, stress
    


@dataclass
class Structure :
    nodes: list
    free_nodes: list
    structure: list
    force: np.ndarray
    model_stress: list
    

    now_truss: list
    critical_buckling_load : list = field(default_factory = list)
    force_heat_map_colour : list = field(default_factory = list)
    now_stress: list = field(default_factory=list)
    axial_list : list = field(default_factory=list)
    prev_truss: list = field(default_factory=list)
    prev_real_displaced_position: list = field(default_factory=list)
    prev_stress: list = field(default_factory=list)

    real_displaced_position: list = field(default_factory=list)
    position_dictionary_real: dict = field(default_factory=dict)

    displacement_ratio: float = 0.0
    estimate_force_scale : float = 0.0
    force_scale: float = 0

    running: bool = True
    collapsed: bool = False

    screenx: int = 800
    screeny: int = 600
    scale: int = 50
    axial_force_full_force_snap_shot : list = field(default_factory=list)
    stress_full_force_snap_shot : list = field(default_factory=list)

    viewing_mode : int = None
    playback_speed: float = 0.1
    timer: float = 0
    display_grid : bool = False
    elapsed_time: float = 0.0
    pause_after_failure : bool = False
    failed_member : tuple =  None

    # ---------- Inspection ----------
    inspection_mode: bool = False
    show_popup: bool = False
    selected_bar: int | None = None

    # ---------- History ----------
    time_history: list = field(default_factory=list)
    stress_history: list = field(default_factory=list)
    axial_force_history: list = field(default_factory=list)


def run_critical_buckling_stress(node,list_of_connections) : 
    critical_stress_list = []
    for connection in list_of_connections : 
        A = connection[2]
        E = connection[3]
        L = np.linalg.norm(np.array(node[connection[0]])-np.array(node[connection[1]]))
        I = (A**2)/(4*np.pi) #assume circular area
        K = 1
        P_cr = np.pi**2*E*I/(L*K)**2
        critical_stress_list.append(P_cr)
    return critical_stress_list






def handle_events(state,structure,editor,camera_object) : 
    for event in pg.event.get():
        if event.type == pg.QUIT:
            structure.running = False

        if event.type == pg.KEYDOWN:

            if event.key == pg.K_RETURN and structure.pause_after_failure:

                remove_failed_member(structure.failed_member,structure.now_truss,
                                     structure.now_stress,structure.axial_list,structure.critical_buckling_load)
                structure.pause_after_failure = False
                structure.failed_member = None
                structure.inspection_mode = False
                structure.show_popup = False
                structure.selected_bar = None
                continue

            if event.key == pg.K_SPACE :
                if state=='simulate' : 
                    structure.collapsed = False
                    structure.now_truss = cp.deepcopy(structure.structure) 
                    structure.now_stress = structure.model_stress.copy()
                    structure.real_displaced_position, structure.displacement_ratio = structure.nodes, 0 #compute_scale(nodes, u_global)
                    structure.position_dictionary_real = node_position_list(structure.screenx, structure.screeny, 
                                                        structure.scale, structure.real_displaced_position,camera_object)
                    structure.colour = structure.model_colour
                    structure.original_buckling_load = run_critical_buckling_stress(editor.node_list,editor.connections)
                    structure.critical_buckling_load = structure.original_buckling_load.copy()
                    structure.timer = 0
                    structure.elapsed_time = 0.0
                    structure.force_scale = 0
                    structure.time_history.clear()
                    structure.stress_history = [[] for _ in range(len(structure.structure))]
                    structure.axial_force_history = [[] for _ in range(len(structure.structure))]
                    structure.pause_after_failure = False
                    structure.failed_member = None

                    #structure.inspection_mode = False
                    #structure.show_popup = False
                    #structure.selected_bar = None
                    

                elif state=='editor':
                    editor.input_force = np.zeros(2*len(structure.nodes))
                    editor.force_vector_list.clear()

            auxillary_condition = (structure.force_scale - structure.estimated_force_scale) < 1e-4 or structure.collapsed or structure.pause_after_failure
            if event.key == pg.K_i and auxillary_condition:
                structure.inspection_mode = not structure.inspection_mode
                if not structure.inspection_mode:
                    structure.show_popup = False
                    structure.selected_bar = None


            if event.key == pg.K_g : 
                if structure.display_grid : structure.display_grid = False
                else : structure.display_grid = True



             ######################3
            if event.key == pg.K_TAB : 
                if state == 'simulate'  : 
                    state = 'editor'
                    structure.display_grid = True
                else :  
                    force_modified = not np.array_equal(structure.force, editor.input_force)
                    node_list_modified = editor.node_list != structure.nodes
                    free_node_list_modified = set(editor.free_node_list) != set(structure.free_nodes)
                    members_modified = set(editor.connections) != set(structure.structure)
                    
                    if node_list_modified or free_node_list_modified or members_modified or force_modified:
                        #reset all node position về ban đầu
                        #bug note : Nếu unstable -> refuse to gán nó cho cái structure. Bởi vì nếu gán cho structure
                        #thì nó tự hiểu là structure ko bị modify khi bấm tab 2 lần liên tục -> không check stability
                        # Chỉ khi stable thì mới gán cho structure. Từng lần chuyển qua simulate phải chắc chắn 100% ổn định
                        #Vì vậy refactor estimate force scale theo hướng không còn OOP chỉ cho obj structure nữa, mà input data
                        try : 
                            structure.original_buckling_load = run_critical_buckling_stress(editor.node_list,editor.connections)
                            structure.critical_buckling_load = structure.original_buckling_load.copy()
                            structure.estimated_force_scale,structure.force_heat_map_colour, structure.axial_force_full_force_snap_shot, structure.stress_full_force_snap_shot = estimate_force_scale(editor.node_list,
                                                                        editor.free_node_list,editor.connections,editor.input_force,structure.critical_buckling_load)
                            structure.real_displaced_position, structure.displacement_ratio = editor.node_list.copy(),0
                            structure.position_dictionary_real = editor.position_dictionary_editor.copy()

                            if node_list_modified : 
                                structure.nodes = editor.node_list.copy()
                                structure.structure = editor.connections.copy()
                            if free_node_list_modified : 
                                structure.free_nodes = editor.free_node_list.copy()
                            if members_modified and not node_list_modified : 
                                structure.structure = editor.connections.copy()
                            if force_modified : 
                                structure.force = editor.input_force.copy()

                            structure.now_stress = structure.model_stress.copy()
                            structure.colour = structure.model_colour.copy()
                            structure.now_truss = structure.structure.copy()
                            structure.timer = 0
                            structure.force_scale = 0
                            structure.collapsed = False #one line fucking fix
                            structure.pause_after_failure = False
                            structure.failed_member = None

                            state = 'simulate'
                            editor.structure_modified = False
                            editor.selecting_vector = None ###
                            editor.moving_vector = False
                            editor.selecting_node = None
                            editor.selecting_node_N = None
                            editor.selecting_bar_N = None
                            editor.creating_bars = False
                            structure.elapsed_time = 0.0
                            structure.time_history.clear()
                            structure.stress_history = [[] for _ in range(len(structure.structure))]
                            structure.axial_force_history = [[] for _ in range(len(structure.structure))]
                            structure.inspection_mode = False
                            structure.show_popup = False
                            structure.selected_bar = None
                        except : 
                            print('Structure unstable, please check again!')


                    else : 
                        state = 'simulate'
                        editor.structure_modified = False
                        editor.selecting_vector = None ###
                        editor.moving_vector = False
                        editor.selecting_node = None
                        editor.selecting_node_N = None
                        editor.selecting_bar_N = None
                        editor.creating_bars = False

            if event.key == pg.K_n and state == 'editor': 
                if editor.structure_editor : 
                    editor.structure_editor = False
                    editor.selecting_node_N = None
                    editor.selecting_bar_N = None
                    editor.creating_bars = False

                else : 
                    editor.structure_editor = True
                    editor.selecting_vector = None
                    editor.selecting_node = None
                    editor.moving_vector = None


            if event.key == pg.K_h and state == 'simulate': 
                structure.viewing_mode +=1
                structure.viewing_mode = structure.viewing_mode%2


        camera_object.handle_clicking(event)
        camera_object.update_zoom(event,structure.screenx,structure.screeny,structure.scale)
        camera_object.update_camera()

        if structure.display_grid :
            structure.generated_lines = generate_grid_lines(camera_object)



        if not structure.collapsed and state == 'simulate': 
            structure.position_dictionary_real = node_position_list(structure.screenx, structure.screeny, structure.scale, 
                                                        structure.real_displaced_position,camera_object)
            
        else : 
            structure.position_dictionary_real = node_position_list(structure.screenx, structure.screeny, structure.scale, 
                                                        structure.prev_real_displaced_position,camera_object)

        if state == 'editor' : 
            editor.position_dictionary_editor = node_position_list(structure.screenx, structure.screeny, 
                                                                   structure.scale, editor.node_list,camera_object)
            #Lưu ý cái position dictionary editor phải work với editor node_list. Lỗi trước đây do làm việc vs
            #structure.nodes nên dictionary editor bị remove, sau đó chạy lại lần nữa nó bị modify theo structure.nodes not editor node_lít
            #chỉ khi nào chuyển sang simulate thì mới bắt đầu gán structure.nodes = editor.node_list
            #Decision editor có bộ node và connection riêng để dễ đối chiếu có đổi structure hay ko ngay cả khi sau nhiều bước xóa làm lại
            editor.update_vector_screen_position(camera_object)

            if editor.structure_editor == False : 
                editor.detect_key_force_editor(event,camera_object)

            else : 
                editor.detect_key_edit_structure(event,structure,camera_object)

        elif event.type == pg.MOUSEBUTTONDOWN and structure.inspection_mode:
            if event.button == 1 : 
                picked = pick_bar(pg.mouse.get_pos(), structure) #return tuple (node1,node2,A1,E1,..)

                if picked is not None:
                    structure.selected_bar = picked
                    structure.show_popup = True
                    #print(structure.selected_bar)

                else:
                    structure.show_popup = False
                    structure.selected_bar = None
    return state




def run_simulation_loop(structure,fixed_dt) : 
    if structure.pause_after_failure:
        return
    if not structure.collapsed and not structure.pause_after_failure:
        structure.timer += 0.0125
        structure.elapsed_time += 0.0125
        structure.force_scale += structure.playback_speed * 0.0167*structure.estimated_force_scale
        structure.force_scale = min(1, structure.force_scale)

        if structure.timer > fixed_dt:
            structure.prev_truss = structure.now_truss.copy()  #cp.deepcopy(structure.now_truss) #
            structure.prev_real_displaced_position = structure.real_displaced_position.copy()
            structure.prev_stress = structure.now_stress.copy()
            structure.timer -= 0.0125
            F_t = structure.force * structure.force_scale


            try:

                u_global, structure.reaction, structure.axial_list, structure.now_stress = solve_truss(
                    structure.nodes,
                    structure.free_nodes,
                    structure.now_truss,
                    F_t
                )

            except:

                print("STRUCTURE HAS COLLAPSED due to singular matrix")
                print("THE % OF FORCE SCALE WAS :", structure.estimated_force_scale*100)
                structure.collapsed = True

            else:

                failed = find_failure(
                    structure.now_truss,
                    structure.now_stress,
                    structure.axial_list,
                    structure.critical_buckling_load
                )

                if failed is not None:

                    structure.pause_after_failure = True
                    structure.failed_member = failed

                    structure.colour = bar_colour(structure)
                    structure.colour[failed] = (140, 0, 180)
                    return

            if not structure.collapsed:
                structure.real_displaced_position,structure.displacement_ratio = compute_scale(structure.nodes, u_global)
                if structure.displacement_ratio>0.2 :
                    print("STRUCTURE HAS COLLAPSED due to displacement ratio")
                    print("THE % OF FORCE SCALE WAS :", structure.force_scale*100)
                    structure.collapsed = True
                    # Additional checking
                else : 
                    if structure.force_scale == 1 : 
                        print("STRUCTURE sustained for the entire load")
                        structure.collapsed = True
                        structure.prev_truss = structure.now_truss.copy() 
                        structure.prev_real_displaced_position = structure.real_displaced_position.copy()
                        structure.prev_stress = structure.now_stress.copy()
                    structure.colour = bar_colour(structure)
                    # -------- Record history --------
                    structure.time_history.append(structure.elapsed_time)
                    for i in range(len(structure.now_truss)):
                        structure.stress_history[i].append(structure.now_stress[i])
                        structure.axial_force_history[i].append(structure.axial_list[i])
                    

def draw_graph(screen, rect, x_data, y_data, font):

    if len(x_data) < 2:
        return

    left_margin = 50
    right_margin = 10
    top_margin = 20
    bottom_margin = 35

    graph = pg.Rect(rect.left+left_margin, rect.top+top_margin,
                    rect.width-left_margin-right_margin,
                    rect.height-top_margin-bottom_margin)

    pg.draw.rect(screen, (255,255,255), graph)
    pg.draw.rect(screen, (40,40,40), graph, 2)

    xmin = x_data[0]
    xmax = x_data[-1]
    if xmax == xmin:
        xmax += 1e-9

    ymin = min(y_data)
    ymax = max(y_data)
    max_abs = max(abs(ymin), abs(ymax))

    if max_abs < 1e5:
        ymin = -1e5
        ymax = 1e5
    else:
        padding = max(0.05*(ymax-ymin), 0.02*max_abs)
        ymin -= padding
        ymax += padding

        if max(y_data) <= 0:
            ymax = min(ymax, 0)

        elif min(y_data) >= 0:
            ymin = max(ymin, 0)

    points = []

    for x, y in zip(x_data, y_data):
        px = graph.left + (x-xmin)/(xmax-xmin)*graph.width
        py = graph.bottom - (y-ymin)/(ymax-ymin)*graph.height
        points.append((px, py))

    pg.draw.lines(screen, (0,120,255), False, points, 2)

    if ymin < 0 < ymax:
        y0 = graph.bottom - (0-ymin)/(ymax-ymin)*graph.height
        pg.draw.line(screen, (180,180,180), (graph.left,y0), (graph.right,y0), 1)

    title = font.render("Stress (MPa)", True, (0,0,0))
    screen.blit(title, (graph.left, rect.top))

    xlabel = font.render("Time (s)", True, (0,0,0))
    screen.blit(xlabel, (graph.centerx-xlabel.get_width()/2, graph.bottom+22))

    for value in [ymax, (ymax+ymin)/2, ymin]:

        py = graph.bottom - (value-ymin)/(ymax-ymin)*graph.height
        pg.draw.line(screen, (0,0,0), (graph.left-5,py), (graph.left,py), 2)

        value_mpa = value/1e6
        if abs(value_mpa) < 0.005:
            value_mpa = 0.0

        txt = font.render(f"{value_mpa:.2f}", True, (0,0,0))
        screen.blit(txt, (graph.left-8-txt.get_width(), py-txt.get_height()/2))

    for value in [xmin, (xmin+xmax)/2, xmax]:

        px = graph.left + (value-xmin)/(xmax-xmin)*graph.width
        pg.draw.line(screen, (0,0,0), (px,graph.bottom), (px,graph.bottom+5), 2)

        txt = font.render(f"{value:.1f}", True, (0,0,0))
        screen.blit(txt, (px-txt.get_width()/2, graph.bottom+8))


def draw_bar_popup(screen, structure,font):

    if structure.selected_bar is None:
        return

    popup_x = 20
    popup_y = 20

    popup_w = 340
    popup_h = 390

    pg.draw.rect(screen,(235,235,235),(popup_x,popup_y,popup_w,popup_h),border_radius=8)

    pg.draw.rect(screen,(30,30,30),(popup_x,popup_y,popup_w,popup_h),width=2,border_radius=8)


    member = structure.selected_bar
    idx = structure.structure.index(member)
    stress = structure.stress_full_force_snap_shot[idx]*structure.force_scale
    axial = structure.axial_force_full_force_snap_shot[idx]*structure.force_scale        
    Pcr = structure.original_buckling_load[idx]
    node1 = np.array(structure.nodes[member[0]])
    node2 = np.array(structure.nodes[member[1]])
    length = np.linalg.norm(node2-node1)


    if stress >= 0:

        ratio = stress/member[4]
        mode = "Tension"

    elif stress == 0 : 
        mode = 'Zero force'
        ratio = 0
    else:
        mode = "Compression"
        sigma_ucs = member[5]        # UCS
        sigma_buckling = (Pcr/ member[2])           # Pcr / A
        sigma_limit = min(sigma_ucs, sigma_buckling) #thường sigma buckling bé hơn
        ratio = abs(stress) / sigma_limit

    text = [

        f"BAR {idx}",

        "",

        f"Mode : {mode}",

        f"Length : {length:.3f} m",

        f"Area : {member[2]:.4f} m^2",

        f"E : {member[3]/1e9:.1f} GPa",

        f"Stress : {stress/1e6:.2f} MPa",

        f"Axial : {axial/1000:.2f} kN",

        f"Euler : {Pcr/1000:.2f} kN",

        f"Load capacity used : {100*ratio:.3f}"]

    y = popup_y + 15

    for line in text:

        surf = font.render(line,True,(20,20,20))

        screen.blit(surf,(popup_x+15,y))

        y += 22
    
    graph_rect = pg.Rect(popup_x + 15,popup_y + 235,popup_w - 30,130)
    draw_graph(screen,graph_rect,structure.time_history,structure.stress_history[idx],font)



def render_simulation(screen_variable, structure, cam,editor,font) : 
    if not structure.collapsed : 
        draw_structure(screen_variable,structure.position_dictionary_real,structure.nodes,structure.free_nodes,
                        structure.now_truss, structure.colour,cam,editor)

    else : 
        if structure.viewing_mode == 0 : 
            draw_structure(screen_variable,structure.position_dictionary_real,structure.nodes,structure.free_nodes,
                       structure.prev_truss,structure.colour,cam,editor)
        else : 
            draw_structure(screen_variable,structure.position_dictionary_real,structure.nodes,structure.free_nodes,
                       structure.prev_truss,structure.force_heat_map_colour,cam,editor)
    if structure.show_popup:
        draw_bar_popup(screen_variable,structure,font)


def display_editor(screen_variable, structure, editor, cam, font):  # recompute model colour

    draw_structure(screen_variable, editor.position_dictionary_editor, editor.node_list,
                   editor.free_node_list, editor.connections,
                   structure.model_colour, cam, editor)

    for force_vector in editor.force_vector_list:
        force_vector.render_fixed_vector(screen_variable, cam)

    if editor.moving_vector:
        editor.draw_mouse_vector(screen_variable, editor.position_dictionary_editor, cam.zoom_factor)

    if editor.creating_bars:
        pg.draw.line(screen_variable, (76,136,255),
                     editor.position_dictionary_editor[editor.begin_node],
                     editor.last_mouse,
                     round(4*cam.zoom_factor))

    if editor.selecting_bar_N is not None:

        panel = pg.Rect(10, 10, 320, 260)
        pg.draw.rect(screen_variable, (240,240,240), panel, border_radius=8)
        pg.draw.rect(screen_variable, (40,40,40), panel, width=2, border_radius=8)

        member = editor.connections[editor.selecting_bar_N]

        lines = [
            f"Selected Bar : {editor.selecting_bar_N}",
            "",
            f"A : {member[2]:.4f} m^2",
            f"E : {member[3]/1e9:.1f} GPa",
            "",
            "[A] Edit Area",
            "[E] Edit Young's Modulus"
        ]

        if editor.editing_bar_property is not None:

            lines.append("")

            if editor.editing_bar_property == "A":
                lines.append("Editing Area")
            else:
                lines.append("Editing Young's Modulus")

            lines.append(f"Input : {editor.input_text}|")

        y = panel.top + 10

        for line in lines:
            surf = font.render(line, True, (20,20,20))
            screen_variable.blit(surf, (panel.left + 10, y))
            y += 22







def run_program(state,structure,editor,camera_object):
    #--------------------------------------------------
    # START PROFILER
    #--------------------------------------------------
    #profiler = cProfile.Profile()
    #profiler.enable()
    #--------------------------------------------------

    pg.init()

    clock = pg.time.Clock()
    screen = pg.display.set_mode((structure.screenx, structure.screeny))
    pg.display.set_caption("Truss game")
    FONT = pg.font.SysFont("consolas",18)
    fixed_dt = 1 / 20

    structure.now_stress = structure.model_stress.copy()
    #now_truss already copied
    structure.real_displaced_position, structure.displacement_ratio = structure.nodes.copy(),0

    structure.position_dictionary_real = node_position_list(structure.screenx,
                                                            structure.screeny,structure.scale,structure.nodes,camera_object)

    editor.intepret_force_array(structure.nodes)
    structure.original_buckling_load = run_critical_buckling_stress(structure.nodes,structure.structure)
    structure.critical_buckling_load = structure.original_buckling_load.copy()
    structure.estimated_force_scale, structure.force_heat_map_colour, structure.axial_force_full_force_snap_shot, structure.stress_full_force_snap_shot = estimate_force_scale(structure.nodes,structure.free_nodes,
                                                                                            structure.now_truss,structure.force,structure.critical_buckling_load)
    structure.colour = bar_colour(structure)
    structure.model_colour = structure.colour.copy()
        # Initialize history buffers
    structure.time_history = []
    structure.stress_history = [[] for _ in range(len(structure.structure))]
    structure.axial_force_history = [[] for _ in range(len(structure.structure))]
    while structure.running:

        state = handle_events(state,structure,editor,camera_object)
        screen.fill((0, 0, 0))

        if state == 'simulate':
            run_simulation_loop(structure, fixed_dt)

        elif state == 'editor':
            pass

        #--------------------------------------------------
        # ALWAYS DRAW
        #--------------------------------------------------

        if structure.display_grid : 
            draw_grid(screen, structure.generated_lines)

        if state == 'simulate':
            render_simulation(screen,structure,camera_object,editor,FONT) 
        else:
            display_editor(screen,structure,editor,camera_object, FONT) 
        #--------------------------------------------------

        pg.display.flip()
        clock.tick(60)

    pg.quit()

    #--------------------------------------------------
    # STOP PROFILER
    #--------------------------------------------------
    #profiler.disable()
    #--------------------------------------------------

    #--------------------------------------------------
    # SAVE RAW PROFILE FILE
    #--------------------------------------------------
    #profiler.dump_stats("profile.prof")
    #--------------------------------------------------

    #--------------------------------------------------
    # PRINT TOP 50 SLOWEST FUNCTIONS
    #--------------------------------------------------
    #stats = pstats.Stats(profiler)

    #stats.sort_stats("tottime")

    #print("\n")
    #print("==================================================")
    #print("                CPROFILE RESULTS")
    #print("==================================================")

    #stats.print_stats(50)

    #print("==================================================")
    #print("\n")
    #--------------------------------------------------


mode = 'simulate'
player = Camera_class(5,3,1)
structure = Structure(nodes = nodes_external, free_nodes = free_nodes_external ,structure = connections ,force = F, now_truss = cp.deepcopy(connections), force_scale = 0
              ,model_stress =[0 for _ in range(0,len(connections))],viewing_mode=0)
editor = Editor(F, nodes_external, free_nodes_external,connections)
run_program(mode,structure, editor,player)
# k : N/m, displacement,world coordinate : m, stress = Pa, internal force : N, strain has no unit, x,y : m.

#data flow & structure decision : 
# the fixed vectors are processed on screen, the force vector is translated to world position
# to preserve invariance so that it can zoom, move when the camera moves.
# And then, for every loop, based on the current zoom and move, the program computes the fixed vector's position on screen
# based on its real position -> zooming, moving effect.