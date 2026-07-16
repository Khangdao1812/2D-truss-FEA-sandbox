# Rendering

## Purpose

   This document aims to provide an overview of the project's rendering pipeline, including coordinate transformations, camera operations and stress-based color mapping.
   


<img width="472" height="596" alt="image" src="https://github.com/user-attachments/assets/726794eb-60d0-4e05-b8ce-ddfef7835198" />


 **An overview of the rendering pipeline**
 
---

## Coordinate Systems
  The application uses two main coordinate systems listed below.
  
### World coordinate
  World coordinates represent the physical structure model. The positive direction of the x-axis points to the right, while that of the y-axis points upwards.

### Screen coordinate
  Screen coordinates represent the positions of structural components (nodes, members, loads, etc.) on the Pygame window. By default, Pygame places the origin at the **top-left corner** of the screen, with the positive x-axis pointing to the right and the positive y-axis pointing downward.

In this project, however, the rendering system redefines the origin to the **center of the bottom edge** of the window. For the default window size of **800 × 600 pixels**, the world-space origin `(0, 0)` is therefore mapped to the screen coordinate **(400, 600)** before panning/zooming is applied.

---

## Camera Transform
  After converting world coordinates into screen coordinates, camera transformations are applied before rendering objects onto the screen.

The camera supports two actions :

- **Translation (Panning):** Moves the viewport by subtracting the camera offsets (`camx`, `camy`) from nodes. -> preserves relative distance under panning
- **Uniform Zooming:** Scales all world coordinates by a common zoom factor while keeping the world position beneath the mouse cursor fixed during zoom operations. -> preserves the scale of relative distances.

Separating camera transformations from world coordinates allows the structural model to remain consistent in size and relative position, as if the user is viewing the world from a limited viewport (which is the pygame window in this case).

---

## Adaptive Grid (optional, can be turned on/off)
  Adaptive grids help users to create nodes more easily, since node creation is limited to only the 1/4 lattice. Their generation begins with determining the quarter-lattice point furthest to the top-left of the screen and transform its position to screen coordinates.
  
  Another calculation determines the number of pixels on screen equivalent to one-quarter of a world unit. Then, the program proceeds to render equally spaced horizontal and vertical lines until they extend beyond the visible screen.

---

## Stress heatmap

   The stress heatmap visualizes the internal force distribution of each element in respect to their calculated failure thresholds. To do this, the function responsible for generating stress heatmap (`bar_colour()`) takes the utilization ratio (`stress/threshold`)for colour-mapping. 
   
   Similarly, force distribution heatmap uses the same mechanism, however, the threshold is now replaced with the maximum/minimum load of an individual member in the entire structure. 
   
  The list of these quantities for all members is then normalized into the range \([0,1]\) before being mapped to an HSV color gradient and converted into RGB values for rendering. This ensures that the entire colour spectrum is utilized for smooth transition between the safe and failure criterion, while also making relative stress differences easier to intepret. 

---

## Clipping

Before rendering each structural member, the program performs line clipping to determine the intersection between a straight member and the viewing port's edges.

Members located entirely outside the screen are ignored, while partially visible members are clipped to the viewport boundaries. The reason for this is to optimize the number of operations and avoid rendering artifacts that previously plagued the rendering system for weeks. 

---
## Drawing
  Repeatedly apply pygame commands like pg.draw_circle and pg.draw_line to render nodes & members.

---
## Performance Considerations

Several optimizations are implemented to maintain smooth performance & save computational capacity for more complex features in the future:

- Grid lines are generated only within the visible viewport.
- Off-screen members are removed through line clipping before rendering.
- Coordinate transformations are performed only when required (when the structure is modifed, for e.g).
