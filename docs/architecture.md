# Architecture


## 1. Purpose
   This is probably the longest document that I'd attached to this project. It presents the overall structure & design of this program for developers who are interested in. By the time you finish reading, you can hopefully get the hang of the entire code & begin adding additional features, upgrades or optimization.
   
### Goals of this document

This document is intended to help readers:

- Understand the overall architecture of the project.
- Build a mental model of how the major subsystems work toghether.
- Guide yourself through the codebase more efficiently.
- Trace the flow of data through the application.
  


## 2. System Overview

### High-level architecture

> [Insert system architecture diagram]

A brief overview of the major subsystems within this project.

### Main subsystems

#### User Interface
Handles user interaction, editing operations, and simulation controls.

#### Simulation Controller
Coordinates the application's execution, manages simulation state.

#### Solver
Computes structural displacements, member forces, and stresses from the current model.

#### Evaluation Engine
Interprets solver outputs, evaluates failure criteria, and updates the simulation state during progressive collapse.

#### Renderer
Visualizes the structure, simulation results, and user interface from the evaluation engine.


---


## 4. Core Concepts

### Structural Model

#### Nodes
Nodes represent the joints of the truss. They define the geometry of the structure and are the locations where supports and external loads can be applied.

#### Elements/member/bar
Elements connect pairs of nodes and model individual truss members. Each element contributes to the global stiffness matrix and carries axial force only.

#### Supports
Supports constrain one or more degrees of freedom of a node and define the boundary conditions of the structure.

#### External Loads
External loads represent forces applied to the structure. They are assembled into the global load vector and drive the structural response.

---

### Simulation State

The simulation maintains a small set of state variables that determine the current behavior of the application.

#### Collapse State
Indicates whether the structure has experienced progressive collapse. When active, the simulation enters a freeze state, allowing the user to inspect the failed structure before continuing without the failed member.

#### Inspection Mode
Provide detailed  structural results, including member force history and other analysis data for every member.

---

### User Interaction

#### Selection
Represents the currently selected node or element. Many editing and inspection operations operate on the current selection.

---

### View

#### Camera
The camera is the lens at which users see the world. Available actions are panning and zooming

---

## 5. Module Architecture
- The modules described below are divided by **LOGICAL RESPONSIBILITY** not individual code files. The project is mainly organized not by subsystems, but by execution states (editor, simulation are the two main ones). Because of this, please bear in mind that a lot of the times, a module's code can spread across many files, and vice versa.


### 5.1 User Interface

**Responsibility**

Handles user input and translates user interactions into editing operations, application state changes, and simulation commands.


**Inputs**

- Application state
- Camera
- Structural model (including the list of nodes, member connections, color-coded map)


**Produces**

- Editing operations
- Selection updates
- Simulation control commands

---


### 5.2 FEM Solver

**Responsibility**

Analyse and compute the structural response using Finite Element Analysis (FEA).

**Inputs**

- Nodes
- Elements
- Supports
- External loads
- Material properties

**Outputs**

- Nodal displacements
- Member forces
- Member stresses

---

### 5.3 Evaluation Engine

**Responsibility**

Evaluates failure conditions using data imported from the solver, and updates the simulation state accordingly (collapsed or not).

**Inputs**

- Solver outputs
- Failure criteria (Ultimate tensile/compressive strength, Euler buckling criterion)

**Outputs**

- Failed members
- Updated simulation state
- Data for visualization

---

### 5.4 Renderer

**Responsibility**

Visualizes the current state of the application by rendering the structural model, analysis results (member color), and user interface (highlights selected bars/nodes/vectors).

**Inputs**

- Structural model
- Evaluation results (% of capacity used)
- Camera (variables such as camx, camy, zoom, scale)

**Outputs**

- Rendered frame

---

## 6. Data Organization & reference sheet.

Reference table for major variables.

| Stored in | Data | Type | Owner (which subsystem) | Consumed by |
|-----------|------|------|-------|-------------|
| `Structure` | Nodes | Mutable | Simulation Controller | FEM Solver, Renderer |
| `Structure` | Elements | Mutable | Simulation Controller | FEM Solver, Renderer |
| `Structure` | Supports | Mutable | Simulation Controller | FEM Solver |
| `Structure` | External Loads | Mutable | Simulation Controller | FEM Solver |
| `Structure` | Nodal Displacements | Derived | FEM Solver | Evaluation Engine, Renderer |
| `Structure` | Member Forces | Derived | FEM Solver | Evaluation Engine, Renderer |
| `Structure` | Member Stresses | Derived | FEM Solver | Evaluation Engine, Renderer |
| `Structure` | Colour code | Derived | FEM Solver | Evaluation Engine, Renderer |
| `Structure` | Failed Members | Derived | Evaluation Engine | Renderer |
| `Camera` | Camera position | Mutable | User Interface | Renderer |
| `Camera` | Zoom | Mutable | User Interface | Renderer |
| `Structure/Editor (1)` | Current Selection | Mutable | User Interface | Renderer |
| `Structure` | Inspection Mode | Mutable | Simulation Controller | Renderer |
| `Structure` | Collapse State | Mutable | Simulation Controller | User Interface, Renderer |

(1) : Detecting the selected object happens in both simulation and editor execution state. They are stored in : 
- structure.selecting_bar : used for detecting which bar to inspect after simulation finished
- editor.selecting_vector : used for detecting which force vector is selected in editor mode
- editor.selecting_node : detecting which node is selected to apply force on to.
- editor.selecting_node_N : detecting which node is selected when the structure is being edited.
- editor.selecting_bar_N : detecting which member is selected when the structure is being edited.

**IMPORTANT NOTE** : You will see the following variables in main.py : 
- nodes_external
- connections
- free_nodes_external
- F_raw
  
  These variables only serve as the external input for the initial demo you see when the program starts. Otherwise, every other actions is documented specifically in the "structure" data class. These include :
  - structure.nodes
  - structure.structure, structure.now_truss
  - structure.free_nodes
  - structure.force

  After the initial startup of the program, the variables nodes_external, connections, free_nodes_external, F_raw will no longer play any role in the program.

The difference between structure.structure and structure.now_truss will be explained later in this document. ######## Jump to the line X if you wish to see it right now.

---

## 7. Core Functions
  For convinience, I'd like to organize this section by each individual code files.

### 1. main.py 

The application's central controller. It owns the main loop, coordinates communication between subsystems, and manages the transition between editor and simulation modes.

---

#### Data type & core functions

#### `Structure` (`@dataclass`)

Stores the complete state of the current truss model and application.

**Contains**

- Nodes and elements
- Supports and external loads
- Analysis results
- Progressive failure state
- Inspection history
- Camera and visualization settings

---

#### Physics & Structural Analysis

| Function | Purpose | Returns |
|----------|---------|---------|
| `run_critical_buckling_stress()` | Computes the Euler critical buckling load for every member. | List of critical buckling loads |
| `estimate_force_scale()` | Predicts the maximum load scale before the first member fails. | Force scale, heat map, axial forces, stresses |
| `find_failure()` | Detects the first member exceeding its failure criterion. | Failed member index or `None` |
| `compute_scale()` | Computes the deformed geometry from nodal displacements. | Deformed node positions, maximum displacement ratio |
| `remove_failed_member()` | Removes a failed member and updates the structural model. | None *(in-place modification)* |
| `run_simulation_loop()` | Advances the simulation by one fixed timestep. | None *(updates the simulation state)* |

---

#### User Interaction

| Function | Purpose | Returns |
|----------|---------|---------|
| `point_segment_distance()` | Computes the shortest distance between the cursor and a bar. | Distance |
| `pick_bar()` | Determines which member is currently selected. | Selected member or `None` |
| `handle_events()` | Processes keyboard and mouse input. | Updated application mode |

---

#### Rendering & User Interface

| Function | Purpose | Returns |
|----------|---------|---------|
| `draw_graph()` | Draws the stress history graph for the selected member. | None |
| `draw_bar_popup()` | Displays detailed information about the selected member. | None |
| `display_editor()` | Renders the editor workspace. | None |
| `render_simulation()` | Renders the simulation scene. | None |
| `run_program()` | Initializes the application and executes the main program loop. | None |




### 2. editor.py

  The user interaction module responsible for constructing and editing truss models. It manages node and member creation, external force editing, coordinate transformations, and mouse-driven interactions within the editor.

---

#### Core Data Structures

#### `Editor` (class)

Manages the editor state, including the editing mode,  selections, and interaction states while constructing or modifying the truss.

#### `ForceVector` (class)

Visual display of an external force applied to a node, storing both its physical magnitude and its graphical representation. It is not a real physical object, though its ending point had to be **stored in world coordinates** to ensure consistent display image under panning/zooming.

---

#### Node Selection & Interaction

| Function | Purpose | Returns |
|----------|---------|---------|
| `pick_closest_node()` | Finds the node closest to the cursor within the threshold. | Selected node index or `None` |
| `find_selected_bar()` | Determines which structural member is currently under/close the cursor. | Selected member index or `None` |

---

#### Structure Editing

| Function | Purpose | Returns |
|----------|---------|---------|
| `detect_key_edit_structure()` | Processes editor input for creating, modifying, and deleting structural components. | None *(updates the structural model)* |
| `detect_key_force_editor()` | Handles mouse interactions for creating and modifying external force vectors. | None *(updates editor state)* |

---

#### Force Vector Management

| Function | Purpose | Returns |
|----------|---------|---------|
| `interpret_force_array()` | Creates `ForceVector` objects from the current global load vector. | None *(updates force vector objects)* |
| `add_force()` | Adds a force vector to the global loading array. | None *(modifies load data in-place)* |
| `remove_force()` | Removes a force vector from the global loading array. | None *(modifies load data in-place)* |

---

#### Rendering & Coordinate Transformation

| Function | Purpose | Returns |
|----------|---------|---------|
| `draw_mouse_vector()` | Renders the temporary force vector preview during drag operations. | None |
| `update_vector_screen_position()` | Updates the screen-space positions of all force vectors after camera movement or zoom. | None |
| `draw_force_vector()` | Draws a standardized force arrow. | None |
| `render_fixed_vector()` | Renders all applied force vectors and their numerical magnitudes. | None |



### 3. solver.py

| Function | Inputs | Returns |
|:---------|:-------|:--------|
| `truss_matrix_elements()` | Node coordinates, cross-sectional area `A`, Young's modulus `E` | Local stiffness matrix, direction cosines (`c`, `s`), `A`, `E`, element length `L` |
| `assemble_to_global()` | Global stiffness matrix, node indices, local stiffness matrix | Updates the global stiffness matrix in-place |
| `connect()` | Node list, element connectivity, material properties, global stiffness matrix | Updates the global stiffness matrix and caches element properties |
| `reduce()` | Global stiffness matrix, global load vector, free DOFs | Reduced stiffness matrix and reduced load vector |
| `global_u()` | Reduced displacement vector, free DOFs, number of nodes | Complete global displacement vector |
| `calculate_axial_force()` | Element identifiers, global displacement vector, cached element properties | Axial force and stress |
| `solve_truss()` | Nodes, supports, element definitions, load vector | Global displacements, reaction forces, axial force list, stress list |

-----------------

The solver follows the classical linear finite element workflow shown below.

| Stage | Function | Responsibility |
|:------|:---------|:---------------|
| **1. Local Element Formulation** | `truss_matrix_elements()` | Compute the local 4×4 element stiffness matrix, direction cosines, and geometric properties. |
| **2. Global Assembly** | `assemble_to_global()` | Assemble a local element stiffness matrix into the global stiffness matrix. |
|  | `connect()` | Generate the local stiffness matrix, assemble it into the global system, and cache element properties for post-processing. |
| **3. Boundary Reduction** | `reduce()` | Apply boundary conditions by extracting the reduced stiffness matrix and load vector using the free DOFs. |
| **4. Linear Solve** | `numpy.linalg.solve()` | Solve the reduced linear system \(K_r u_r = F_r\). |
| **5. Displacement Reconstruction** | `global_u()` | Reconstruct the complete global displacement vector by inserting zero displacements at constrained DOFs. |
| **6. Post-processing** | `calculate_axial_force()` | Compute element strain, stress, and axial force using the solved global displacement vector. |
| **7. Solver Driver** | `solve_truss()` | Coordinate the entire solution pipeline and return all analysis results. |




### 4. visualization.py

Handles coordinate transformations and structural visualization.

---

#### Coordinate Mapping

| Function | Purpose | Returns |
|:---------|:---------------|:--------|
| `transform_coordinate()` | Convert world coordinates into screen coordinates using the current camera position and zoom level. | Screen-space `(x, y)` |
| `convert_screen_to_world()` | Convert screen coordinates back into world coordinates. | World-space `(x, y)` |
| `node_position_list()` | Transform every structural node into screen space and build a lookup table. | Dictionary of screen positions |
| `snap_quarter()` | Snap a world coordinate to the nearest 0.25-unit grid interval. | Snapped coordinate (a value) |
| `line_clip()` | Clip line segments against the visible viewport. | Clipped endpoints or `False` |

---

#### Heatmap & Color Processing

| Function | Purpose | Returns |
|:---------|:---------------|:--------|
| `hsv_to_rgb()` | Convert HSV values into RGB values. | RGB tuple |
| `bar_colour()` | Generate member colors based on structural state and failure information. | List of RGB colors |
| `calculate_force_heatmap()` | Generate a force heatmap using red for tension and blue for compression. | List of RGB colors |

---

#### Rendering

| Function | Purpose | Returns |
|:---------|:---------------|:--------|
| `draw_structure()` | Render nodes, members, supports, selections, and editor overlays onto the screen. | None |
| `generate_grid_lines()` | Generate adaptive grid lines according to the current zoom level. | Grid line data |
| `draw_grid()` | Render the generated background grid. | None |

---

#### Rendering task

| Component | Purpose |
|:----------|:---------------|
| Coordinate Mapping | Convert between world and screen coordinate. |
| Heatmaps | Visualize structural stress and force distributions. |
| Grid System | Generate and render an adaptive engineering grid. |
| Structure Rendering | Draw nodes, members, supports, and editor overlays. |



### 5. camera.py

Manages the viewport's navigation, including panning, zooming, and camera state.

---

##### Core Data Structure

#### `Camera` (class)
Stores viewport translation (`camx`, `camy`), zoom level, scaling limits, and interaction states used for camera movement.

---

#### Camera Controls

| Method | Responsibility | Returns |
|:-------|:---------------|:--------|
| `handle_clicking()` | Start or stop viewport dragging and cache the initial mouse position. | None |
| `update_camera()` | Update the camera position during click-and-drag panning and ensure constraints of the camera's position. | None |
| `update_zoom()` | Adjust the zoom level while keeping the world position under the cursor fixed on the screen. | None |


-----
## 8. Proram cycle

### Program startup

### Normal frame

### Solving a structure

### Progressive failure

### Inspection workflow

---


## 9. Typical Workflows

1. Creating a bridge

2. Applying a load

3. Running the simulation

4. Inspecting a member

5. Progressive collapse

---

## 10. Extension Points

| I want to... (goal) | Primary Modules |
|:------|:----------------|
| Add a new UI tool | `editor.py`, `main.py` |
| Add a new visualization for buckling| `visualization.py`, `main.py` |
| Replace the renderer | `visualization.py` |
| Add a new failure criterion | `main.py` |
| Add a new structural element | `solver.py`, `visualization.py`, `editor.py` |
| Replace the linear solver | `solver.py` |
| Add simulation controls | `main.py` |

---

## 11. Suggested improvements in code architecture

The current architecture prioritizes feature development over ideal software organization. The following areas are recognised for future refactoring : 

- The `Structure` dataclass currently stores several runtime variables (`timer`, `elapsed_time`, `pause_after_failure`, `time_history`, `selected_bar`, etc.) that are unrelated to the structural model. Simulation state, UI state, and structural data should eventually be separated into dedicated classes.

- Structural nodes and members are represented as tuples gathered in a list rather than `Node` and `Element` objects. This leads to frequent index arithmetic, reduces readability, and makes future extensions more difficult.

- Switching between editor and simulation modes requires manually resetting numerous variables, clearing multiple lists, and copying structural data. A cleaner design would replace or reinitialize the entire `Structure` object in the main program loop, significantly simplifying state management.

- Heavy reliance on state variables like : moving_vector (turns on when in the load editor) , inspection_mode, creating bars (turns on when in the structure editor), etc. There are many variables that are dependent on these states and require manual reset each time the main states turn on or off.
