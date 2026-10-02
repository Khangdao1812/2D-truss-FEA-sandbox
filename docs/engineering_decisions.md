# Engineering Decisions

## Purpose
 This document is a collection of decisions related to the technicalities throughout the long journey of creating this project. 

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
- Keeps the implementation focused on ideas & modeling in structural engineering rather than optimizing computation
- Makes the code more readable to developers (especially when numpy is a well-known library)

**Trade-offs** : 
- Dependency on code library

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
- Avoids long and confusing code when working with index arithmetic.

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

---
## Math & other
---
### Why calculate the precise failure load instead of using fixed load increments?
Instead of increasing the applied load by fixed increments, the simulation computes the exact load scale at which the next structural member fails.

**Reason** : 
- Prevents missing the exact failure point due to crude load increments.
- Removes the need to balance accuracy against simulation speed through manual adjustments.
- Ensures consistent speed and accuracy regardless of the different geometries.
  
**Trade-offs** : 
- Slightly increases implementation complexity
- Limit : Only applicable when working with linear elastic assumption, meaning all deformations can be recovered when forces are removed.

---
### Why discrete time step?
The simulation advances through discrete time steps rather than using a continuous time flow (which would require integrands).

**Reason** : 
- Matches the event-driven nature of the progressive failure mechanism in the program.
- Simplifies animation playback and time-history recording.

**Trade-offs** : 
- Does not capture continuous structural behaviour.
- Motion between states is approximated through discrete updates.

---
### Why non-rotatable camera?
Camera actions are limited to panning and uniform zooming only

**Reason** : 
- Avoids complex coordinate calculations involving rotation matrices
- Eliminates the need to recalculate slopes and angles of force vectors for every frame.


