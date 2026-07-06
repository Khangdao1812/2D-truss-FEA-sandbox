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
Indicates whether the structure has experienced progressive collapse. When active, the simulation enters a freeze state, allowing the user to inspect the failed configuration before continuing without the failed member.

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

### main.py 

The application's central controller. It owns the main loop, coordinates communication between subsystems, and manages the transition between editor and simulation modes.

---

#### Core Data Structure

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
| `point_segment_distance()` | Computes the shortest distance between the cursor and a member. | Distance |
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



-----
## 7. Execution Flow

### Program startup

### Normal frame

### Solving a structure

### Progressive failure

### Inspection workflow

---

## 8. Communication Between Modules

Who calls whom?

Dependency direction

Data flow

---

## 9. Typical Workflows

Creating a bridge

Moving a node

Applying a load

Running the simulation

Inspecting a member

Progressive collapse

---

## 10. Extension Points

Adding new UI tools

Adding new element types

Replacing the renderer

Changing the solver

Adding new visualization

---

## 11. Architectural Constraints

Current assumptions

Known limitations

Future scalability
