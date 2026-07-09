# Engineering Decisions

## Purpose
 This document is a collection of decisions related to the technical aspect of this project throughout the long journey. 

## Solver design

### Why 2D, linear elastic truss analysis?
The program only supports the analysis of planar truss structures, assuming small deformation and deformations remain in the elastic region of the stress-strain graph

**Reason** : 
- Provides an approachable introduction to finite-element-analysis
- Keeps the solver compact and easy to understand
- Covers many highschool mathematical concepts (vectors, dot products, etc) and a variety of bridge, roof structures
- Introduces convinient computational shortcuts as discussed in the **Math & other** section.

**Trade-off** : 
- Deformations beyond the elastic region are not accounted
- Can not model beam behaviours
- Limited to 2D plane
---
### Why NumPy instead of writing custom matrix operations?
NumPy is used for all matrix assembly and linear algebra operations.

**Reason** : 
- Keeps the implementation focused on ideas & modeling in structural engineering rather than numerical optimization
- Makes the code more readable to general developers (especially when numpy is a well-known library)

**Trade-offs** : 
- Dependency on code library
- Does not illustrate understanding of linear algebra down to the deepest levels

---
### Why dictionary-based element look up?
Node positions are mainly stored in dictionaries.

**Reason** : 
- Straight forward key-value look up
- O(1) time complexity for look ups

**Trade-offs** : 
- Requires careful & consistent organization of key-value pairs

---
## Architecture
---
### Why introduce OOP?
Object-oriented programming is used selectively in some areas of the project. For example : Editor, Structure (@dataclass), Camera, force_vector

**Reason** : 
- Keeps related data and behaviors together, improving code organization and readability.
- Simplifies communication between different parts of the program.
- Avoids long and confusing code when working solely with lists, tuples and indices.

**Trade-offs**
- Some runtime variables (such as playback_speed, time, etc) is currently concentrated within the `Structure` class, increasing coupling.
---
## Rendering
---
### Why load and stress heatmaps?
The program provides two visualization modes: a load ratio heatmap indicating structural utilization and a stress heatmap showing the internal force in each member.

**Reason** : 
- Load ratio provides a display of structural safety by highlighting members approaching their failure limits with colors intuitive to people's perception of safety
- Stress visualization helps users understand how forces are distributed throughout the structure.
- Switching between both modes allows users to view simulation results from multiple perspectives.
- For example, stress heatmap may provide specific details about safety & failure, while load ratio heatmap can be used to help engineers decide which member to pay closer attention to in the future due to heavier loads.

**Trade-offs** : 
- Requires maintaining two independent color-mapping strategies.
- Users must understand the difference between stress and utilization to interpret the results correctly.

---
## Math & other

### Why calculate the precise failure load instead of using fixed load increments?
Instead of increasing the applied load by fixed increments, the simulation computes the exact load scale at which the next structural member fails.

**Reason** : 
- Prevents missing the exact failure point due to crude load increments.
- Obviates the need to balance accuracy against simulation speed through manual adjustments.
- Ensures consistent and deterministic progressive failure behavior regardless of the structure geometry and chosen playback speed.

**Trade-offs** : 
- Requires additional calculations before each failure event.
- Slightly increases implementation complexity
- Only applicable under the assumption of small deformation in the material's elastic region.

---
### Why discrete time step?
The simulation advances through discrete time steps rather than using advanced continuous time integration.

**Reason** : 
- Matches the event-driven nature of the progressive failure mechanism in the program.
- Simplifies animation playback and time-history recording.
- Allows each analysis step to reach equilibrium before advancing to the next event.

**Trade-offs** : 
- Does not capture continuous structural dynamics or inertial effects.
- Motion between states is approximated through discrete updates.

---
### Why non-rotatable camera?
Camera actions are limited to panning and uniform zooming only

**Reason** : 
- Avoids complex coordinate calculations involving rotation matrices
- Eliminates the need to recalculate slopes and angles of force vectors for every frame.


