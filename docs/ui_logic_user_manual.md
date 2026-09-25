# UI Logic

The user interface is built around two main states: **Structure Editing** and **Force Editing**. The editor maintains its own copy of the node list, free-node list, connections, and force data until the user switches to simulation. This separation allows the structure to be modified without immediately changing the active simulation model.

## 1. Coordinate System and Camera

The interface uses a camera system to convert between screen coordinates and physical/world coordinates. The camera supports panning by dragging and zooming with the mouse wheel. Zooming is centered around the current mouse position so that the point under the cursor remains visually stable.

When creating or selecting structural elements, screen coordinates are converted back into world coordinates. New nodes are snapped to the nearest quarter-unit lattice, giving the user a consistent way to construct the truss.

## 2. Structure Editing

In structure-editing mode, the user can create and modify nodes and members.

A middle-click creates a node at the nearest lattice position. If the location already contains a node, the same interaction toggles whether that node is constrained or free. Each newly created node also receives a corresponding pair of force degrees of freedom initialized to zero.

Members are created by selecting a starting node and then selecting an ending node. A new member is assigned default material and geometric properties, which can later be edited.

Nodes and members can also be selected for editing or deletion. Member selection uses the shortest distance from the mouse position to the member segment rather than requiring the user to click exactly on the line.

## 3. Member Properties

After selecting a member, the user can edit its cross-sectional area or Young's modulus using the keyboard.

Pressing `A` enters cross-sectional-area editing, while `E` enters Young's-modulus editing. The value is entered as text and committed with `Enter`. Invalid input is ignored, while `Escape` cancels the edit.

## 4. Force Editing

Force vectors are edited separately from the structural geometry. The user selects a node and drags to define the direction and magnitude of the applied force. The force vector is converted into numerical horizontal and vertical components before being passed to the solver.

Existing force vectors can be selected and removed with `Backspace`. Their screen positions are recalculated whenever the camera changes so that they remain attached to the corresponding nodes.

## 5. Simulation and Visualization

Once editing is complete, the editor's model is transferred to the simulation state. The solver then operates on the resulting structural model rather than directly on the UI representation. The calculated displacements, axial forces, stresses, and failure-related quantities are subsequently used by the visualization system.

The visualization can display structural behavior using different modes, including force-based and stress/utilization-based heatmaps. Member colors are calculated from the corresponding analysis results, allowing areas of high structural demand to be identified visually.

## 6. Overall Interaction Flow

```text
User Input
   ↓
Camera / Coordinate Conversion
   ↓
Editor State
   ├── Nodes
   ├── Members
   ├── Supports
   └── Forces
   ↓
Transfer to Simulation Model
   ↓
FEA Solver
   ↓
Displacements / Forces / Stresses
   ↓
Visualization
```

The UI therefore acts as the interface between the physical model the user wants to analyze and the numerical representation required by the finite-element solver.

