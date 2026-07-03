## THE CORE SOLVER

A quick look at the master function of the solver : 

<img width="908" height="665" alt="image" src="https://github.com/user-attachments/assets/0e677145-3553-4d47-97b4-9ba40bc97977" />


Before we begin, there are a few assumptions in this project that should be addressed first.

# Assumptions & limitations : 
- Bars can have different cross sectional area & Young's modulous but they have to be all uniform
- Assume we do not permit rotation about each node
- No deformation, the bar breaks or remains




# From Hooke's law to linear algebra model
   At the very beginning, everything comes from a simple physical idea: if you pull on a bar, it stretches. If you push on it, it compresses. Remember the good old Hooke's law? 
Hooke’s law says that force is proportional to deformation. For a 1D bar:

F = k * ΔL

where ΔL is the change in length, and k is the stiffness of the bar. For a uniform bar, stiffness is:

k = EA / L

So we can write:

F = (EA / L) * ΔL


## Step 1: What is ΔL in a truss?

In a truss, elements are not aligned with the x or y axis. Each element is oriented in 2D space. So, how do we compute the change in length ΔL from node displacements?

Let node i have coordinates (x_i, y_i) and node j have coordinates (x_j, y_j).

The original element has a direction vector:

d = (x_j - x_i, y_j - y_i)

Let its length be L, and define direction cosines:

c = (x_j - x_i) / L  
s = (y_j - y_i) / L  

The vector (c, s) is the unit vector in the direction of the bar.

Now let the nodal displacements be:

Node i : (u_i, v_i)  
Node j : (u_j, v_j)

Instead of thinking in x and y separately, we project the **relative displacement** onto the element's axis using the dot product.

The extension ΔL is:

ΔL = (u_j - u_i)c + (v_j - v_i)s

Still simple.... Right?

This is the first important step: it converts 2D motion into a 1D stretch along the element.


## Step 2: From extension to force

We have the following fundamental equations:

- Axial strain : ε = ΔL / L (no unit)
- Hooke's Law : σ = Eε (E is Young's modulus, σ is stress)
- F = σA (A is the cross-sectional area)

With a bit of algebraic manipulation, we have:

F = σA = EεA = EA*ΔL / L

Now plug ΔL into Hooke's law:

F = (EA / L) * [(u_j - u_i)c + (v_j - v_i)s]

This F is the internal axial force in the element.


## Step 3: Distribute forces to nodes

The element pulls equally and oppositely on its two nodes.

At node i, the force is in the negative direction of the element.

At node j, the force is in the positive direction.

We project F back into the x and y axis:

At node i:

F_ix = -F * c

F_iy = -F * s

At node j:

F_jx = F * c

F_jy = F * s

Now substitute F:

F_ix = -(EA / L) * [(u_j - u_i)c + (v_j - v_i)s] * c

F_iy = -(EA / L) * [(u_j - u_i)c + (v_j - v_i)s] * s

F_jx = (EA / L) * [(u_j - u_i)c + (v_j - v_i)s] * c

F_jy = (EA / L) * [(u_j - u_i)c + (v_j - v_i)s] * s

## Step 4: Rewriting in matrix form

Now comes the key transition to a different expression which allows us to utilize computational power.

Start from the expression of the axial force:

F = (EA / L) * [(u_j - u_i)c + (v_j - v_i)s]

Now look at the force components at node i:

F_ix = -F * c

F_iy = -F * s

Substitute F into F_ix:

F_ix = -(EA / L) * [(u_j - u_i)c + (v_j - v_i)s] * c

Now distribute c into the bracket:

F_ix = -(EA / L) * [(u_j - u_i)c² + (v_j - v_i)cs]

Now expand the differences:

F_ix = -(EA / L) * [u_jc² - u_ic² + v_jcs - v_ics]

Rearrange by grouping terms for each node:

F_ix = (EA / L) * [u_ic² + v_ics - u_jc² - v_jcs]

Do the same for F_iy, we get:

F_iy = (EA / L) * [u_ics + v_is² - u_jcs - v_js²]

Do the same for node j.

OBSERVE THAT:

Each force component is a linear combination of the four displacement variables:

u_i, v_i, u_j, v_j

For example:

F_ix = (EA / L) * [(c²)u_i + (cs)v_i + (-c²)u_j + (-cs)v_j]

F_iy = (EA / L) * [(cs)u_i + (s²)v_i + (-cs)u_j + (-s²)v_j]

Looking at each individual equation, can you recognize the matrix-vector multiplication?

On the left, group the forces:

[F_ix, F_iy, F_jx, F_jy], denote it as F_e

On the right, group the displacements:

[u_i, v_i, u_j, v_j], denote it as u_e

See it? We rewrite the entire system compactly:

F_e = k_e u_e

Where k_e is:

k_e = (EA / L) *

[
 [ c²,  cs, -c², -cs ],
 [ cs,  s², -cs, -s² ],
 [ -c², -cs,  c²,  cs ],
 [ -cs, -s²,  cs,  s² ]
]

Does this look more familiar now? 

<img width="473" height="281" alt="image" src="https://github.com/user-attachments/assets/98bc9b75-12b8-4d13-813a-b75ef6021034" />


This step is insightful, allowing computational power to come into play. "Magic!!!"

So the scary matrix form is rather a more sophisticated way to encode such a mess of variables and equations.


## Step 5: Generalized case

Each element only connects two nodes, but a structure has many elements.

We define a global displacement vector u:

u = [u₁, v₁, u₂, v₂, ..., uₙ, vₙ]

Each element contributes its k_e into a global stiffness matrix K.

This process is called assembly:

- map local DOFs → global DOFs
- add k_e into the correct positions in K

After assembling all elements, we get:

Ku = F

This is the entire linear system.

Challenge : Can you see & feel the mapping between local DOFS -> local DOFs? 
<img width="566" height="221" alt="image" src="https://github.com/user-attachments/assets/7bf8fbf6-cbb3-4e5c-9d39-1d10fc1c9a37" />



## Step 6: Stress, strain, axial force, and the others...

We're discussing the job of this block : 
<img width="821" height="167" alt="image" src="https://github.com/user-attachments/assets/b4e47e82-b9a2-4b1c-b1fe-2739bf88d6d9" />

What can we compute after solving for nodal displacements?

### 1. Element extension

For each element:

ΔL = (u_j - u_i)c + (v_j - v_i)s

This tells us how much the element stretches or compresses.

### 2. Axial force

Using Hooke's law:

F = (EA / L) * ΔL

This gives the internal force in each bar.

Positive means tension, negative means compression.

### 3. Stress

We can compute stress:

σ = F / A

This tells us how "intense" the force is inside the material. This determines if the bar will collapse, not merely the axial force.

### 4. Reaction forces

Even though we remove constrained DOFs when solving, we can recover reaction forces at supports.

Plug the full displacement vector back into:

F = Ku

The entries corresponding to fixed DOFs give the reaction forces.

- NumPy provides convenient operations for yielding reduced matrices and reconstructing the full displacement vector.

