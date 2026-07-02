# 2D truss-solving FEA sandbox
A 2D Truss FEA Sandbox

<img width="970" height="620" alt="Animation" src="https://github.com/user-attachments/assets/042ee741-2630-4d72-adba-6377a39b2826" />


## Overview

This project is an interactive 2D truss finite element analysis (FEA) sandbox that allows users to build and experiment with custom truss structures. Users can create nodes and members, define support conditions, and apply external nodal loads to investigate structural behavior.

The solver computes nodal displacements, internal member forces, and stresses using the global stiffness matrix method. Results are visualized through color-coded stress maps, and interactive inspection tools, with a particular emphasis on the intuitive aspect of structural engineering. The project also supports progressive structural failure simulation, enabling users to observe how their structure would collapse in reality to a certain degree of accuracy, though exact behaviour is not guaranteened due to initial assumptions discussed near the end. 

<img width="970" height="721" alt="Project_graph" src="https://github.com/user-attachments/assets/90def593-7294-4425-9fd5-d16d25492947" />

Progressive failure frame-freeze : Every time the user hits the enter button, the failed member is removed and the program resolves for the force & stress distribution. The darker a member is, the closer it is to failing completely.

<img width="970" height="721" alt="Project_progressive failure" src="https://github.com/user-attachments/assets/cae49789-ab3a-41c2-aac1-6dd1ebf72677" />

----------------------------------------

## Motivation

  Around a year ago, I borrowed an old book of my grandparents about classical mechanics in engineering (they're both civil engineers) and was particularly intrigued with the content and the exercise. Prior to this, I've also explored some engineering softwares like CAD and SolidWorks out of curiosity. However, the experience was not so smooth since their interface is not so straightforward to a my 14-year-old self (I also don't see the reason why they should optimize it for a 14-year-old!).
   One day, these two thoughts, combined with my pursuit in linear algebra at the time, came toghether unexpectedly after wandering around the corners of my mind. This is the reason why I set out to program THIS engineering sandbox on my own, with the aim to both learn & make structural analysis more accessible to young engineering enthusiasts

→ Read more: docs/Reflection.md

----------------------------------------

## Features

- Interactive 2D truss editor (load, member, node creation)
- Configurable support conditions
- Linear elastic finite element analysis (global stiffness method)
- Real-time deformation visualization
- Axial force and stress computation
- Color-coded member stress visualization
- Member inspection panel with detailed properties
- Progressive member failure simulation
- Tensile and compressive failure criteria
- Buckling visualization for compression members
- Freeze-frame collapse inspection
- Stepwise load scaling
- Deterministic failure sequence
- Euler buckling criterion


----------------------------------------

## How it works

# Core pipeline : 

Node
↓
Element
↓
Global stiffness matrix
↓
Boundary conditions
↓
Solve
↓
Post-processing
↓
Visualization

→ Read more: docs/architecture.md

----------------------------------------

## Core algorithm

- Involves stiffness matrix assembly in Finite Element Analysis
- Linear algebra involved (+vector geometry in interface processing)

→ Read more: docs/fem_solver.md

----------------------------------------

## User Interface

<img width="970" height="721" alt="Project_editor" src="https://github.com/user-attachments/assets/45aab051-7031-4e37-a6dd-1e917f389026" />


The interface is organized for a simple workflow : build -> simulate -> post-mortem inspection

Editing tools are available before the simulation begins, allowing users to create nodes and members, assign fixed supports, apply loads, and modify structural properties. Once a simulation starts, the model is locked to ensure a consistent finite element analysis.

Simulation results can be explored through the property inspector, stress visualization, and deformation display. During progressive failure analysis, failed members remain visible in a freeze-frame state, allowing users to inspect each collapse event before advancing to the next simulation step.

For a detailed explanation of the interface design and interaction principles, see docs/ui_logic_user_manual.md .

→ Read more: docs/ui_logic_user_manual.md

----------------------------------------

## Typical Applications

• Bridge trusses
• Roof trusses
• Educational examples
• Small structural studies


----------------------------------------

## Limitations

• 2D only
• Truss only
• Linear elastic
• Small deformation


----------------------------------------

## Future Work

- Extend to 3D FEA
- Modeling non-linear behaviour of materials
- Accurate buckling and yielding visualization
- Library of properties of commonly found material in engineering
- Dynamic & Kinematics Analysis
- Distributed load

----------------------------------------

## Documentation

• Architecture
• Engineering_decisions
• UI_logic_user_manual
• Rendering
• Reflection
- Core solver

----------------------------------------

## Acknowledgements
- I would like to thank the following people/websites for providing me resources to build this project :
  + Grand Sanderson (owner of 3Blue1Brown) for his amazing series on the essence of linear algebra :
  + https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab
  + w3schools.com for providing helpful information on python syntax
  + This pdf textbook on the fundamentals of FEA : http://freeit.free.fr/Finite%20Element/Hutton%20-%20Fundamentals%20of%20FEA,%202004/Chapter%202.PDF
