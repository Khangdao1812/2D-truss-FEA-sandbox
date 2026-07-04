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

$$F = k \Delta L$$

where $\Delta L$ is the change in length, and $k$ is the stiffness of the bar. For a uniform bar, stiffness is:

$$k = \frac{EA}{L}$$

So we can write:

$$F = \left(\frac{EA}{L}\right) \Delta L$$


## Step 1: What is $\Delta L$ in a truss?

In a truss, elements are not aligned with the x or y axis. Each element is oriented in 2D space. So, how do we compute the change in length $\Delta L$ from node displacements?

Let node $i$ have coordinates $(x_i, y_i)$ and node $j$ have coordinates $(x_j, y_j)$.

The original element has a direction vector:

$$d = \begin{bmatrix} x_j - x_i \\ y_j - y_i \end{bmatrix}$$

Let its length be $L$, and define direction cosines:

$$c = \frac{x_j - x_i}{L}$$  
$$s = \frac{y_j - y_i}{L}$$  

The vector $\begin{bmatrix} c \\ s \end{bmatrix}$ is the unit vector in the direction of the bar.

Now let the nodal displacements be:

Node $i$: $(u_i, v_i)$
Node $j$: $(u_j, v_j)$

Instead of thinking in x and y separately, we project the **relative displacement** onto the element's axis using the dot product.

The extension $\Delta L$ is:

$$\Delta L = (u_j - u_i)c + (v_j - v_i)s$$

Still simple.... Right?

This is the first important step: it converts 2D motion into a 1D stretch along the element.


## Step 2: From extension to force

We have the following fundamental equations:

- Axial strain : $\varepsilon = \frac{\Delta L}{L}$ (no unit)
- Hooke's Law : $\sigma = E\varepsilon$ ($E$ is Young's modulus, $\sigma$ is stress)
- $F = \sigma A$ ($A$ is the cross-sectional area)

With a bit of algebraic manipulation, we have:

$$F = \sigma A = E\varepsilon A = \frac{EA \Delta L}{L}$$

Now plug $\Delta L$ into Hooke's law:

$$F = \frac{EA}{L} [(u_j - u_i)c + (v_j - v_i)s]$$

This $F$ is the internal axial force in the element.


## Step 3: Distribute forces to nodes

The element pulls equally and oppositely on its two nodes.

At node $i$, the force is in the negative direction of the element.

At node $j$, the force is in the positive direction.

We project $F$ back into the x and y axis:

At node $i$:

$$F_{ix} = -F \cdot c$$

$$F_{iy} = -F \cdot s$$

At node $j$:

$$F_{jx} = F \cdot c$$

$$F_{jy} = F \cdot s$$

Now substitute $F$:

$$F_{ix} = -\frac{EA}{L} [(u_j - u_i)c + (v_j - v_i)s] c$$

$$F_{iy} = -\frac{EA}{L} [(u_j - u_i)c + (v_j - v_i)s] s$$

$$F_{jx} = \frac{EA}{L} [(u_j - u_i)c + (v_j - v_i)s] c$$

$$F_{jy} = \frac{EA}{L} [(u_j - u_i)c + (v_j - v_i)s] s$$

## Step 4: Rewriting in matrix form

Now comes the key transition to a different expression which allows us to utilize computational power.

Start from the expression of the axial force:

$$F = \frac{EA}{L} [(u_j - u_i)c + (v_j - v_i)s]$$

Now look at the force components at node $i$:

$$F_{ix} = -F \cdot c$$

$$F_{iy} = -F \cdot s$$

Substitute $F$ into $F_{ix}$:

$$F_{ix} = -\frac{EA}{L} [(u_j - u_i)c + (v_j - v_i)s] c$$

Now distribute $c$ into the bracket:

$$F_{ix} = -\frac{EA}{L} [(u_j - u_i)c^2 + (v_j - v_i)cs]$$

Now expand the differences:

$$F_{ix} = -\frac{EA}{L} [u_jc^2 - u_ic^2 + v_jcs - v_ics]$$

Rearrange by grouping terms for each node:

$$F_{ix} = \frac{EA}{L} [u_ic^2 + v_ics - u_jc^2 - v_jcs]$$

Do the same for $F_{iy}$, we get:

$$F_{iy} = \frac{EA}{L} [u_ics + v_is^2 - u_jcs - v_js^2]$$

Do the same for node $j$.

OBSERVE THAT:

Each force component is a linear combination of the four displacement variables:

$u_i$, $v_i$, $u_j$, $v_j$

For example:

$$F_{ix} = \frac{EA}{L} [(c^2)u_i + (cs)v_i + (-c^2)u_j + (-cs)v_j]$$

$$F_{iy} = \frac{EA}{L} [(cs)u_i + (s^2)v_i + (-cs)u_j + (-s^2)v_j]$$

Looking at each individual equation, can you recognize the matrix-vector multiplication?

On the left, group the forces into an element force vector $F_e$:

$$
F_e=
\begin{bmatrix}
F_{ix}\\
F_{iy}\\
F_{jx}\\
F_{jy}
\end{bmatrix}
$$

On the right, group the displacements into an element displacement vector $u_e$:

$$
u_e=
\begin{bmatrix}
u_i\\
v_i\\
u_j\\
v_j
\end{bmatrix}
$$

See it? We rewrite the entire system compactly:

$$F_e = k_e u_e$$

Where $k_e$ is the $4 \times 4$ element stiffness matrix:

$$k_e = \frac{EA}{L} \begin{bmatrix}
c^2 & cs & -c^2 & -cs \\
cs & s^2 & -cs & -s^2 \\
-c^2 & -cs & c^2 & cs \\
-cs & -s^2 & cs & s^2
\end{bmatrix}$$

Does this look more familiar now? 

<img width="473" height="281" alt="image" src="https://github.com/user-attachments/assets/98bc9b75-12b8-4d13-813a-b75ef6021034" />


This step is insightful, allowing computational power to come into play. "Magic!!!"

So the scary matrix form is rather a more sophisticated way to encode such a mess of variables and equations.

**IMPORTANT NOTE** : You might have seen the Load graph in the inspection mode (shown in the [README](https://github.com/Khangdao1812/2D-truss-FEA-sandbox/blob/main/README.md) ) and asked why does it have the shape of a line. Now you know it! This project is all based on assuming **linear** elastic behaviour, meaning that force is proportional to deformation (Hooke's law mentioned above). The load itself is also applied linearly over time as a simulation choice, which keeps the response within the assumptions of the solver.

## Step 5: Generalized case

Each element only connects two nodes, but a structure has many elements.

We define a global displacement vector $u$:

$$
u=
\begin{bmatrix}
u_1\\
v_1\\
u_2\\
v_2\\
\vdots\\
u_n\\
v_n
\end{bmatrix}
$$

Each element contributes its $k_e$ into a global stiffness matrix $K$.

This process is called assembly:

- map local DOFs → global DOFs
- add $k_e$ into the correct positions in $K$

After assembling all elements, we get:

$$Ku = F$$

This is the entire linear system.

Challenge : Can you see & feel the mapping between local DOFS -> local DOFs? 
<img width="566" height="221" alt="image" src="https://github.com/user-attachments/assets/7bf8fbf6-cbb3-4e5c-9d39-1d10fc1c9a37" />



## Step 6: Stress, strain, axial force, and the others...

We're discussing the job of this block : 
<img width="821" height="167" alt="image" src="https://github.com/user-attachments/assets/b4e47e82-b9a2-4b1c-b1fe-2739bf88d6d9" />

What can we compute after solving for nodal displacements?

### 1. Element extension

For each element:

$$\Delta L = (u_j - u_i)c + (v_j - v_i)s$$

This tells us how much the element stretches or compresses.

### 2. Axial force

Using Hooke's law:

$$F = \frac{EA}{L} \Delta L$$

This gives the internal force in each bar.

Positive means tension, negative means compression.

### 3. Stress

We can compute stress:

$$\sigma = \frac{F}{A}$$

This tells us how "intense" the force is inside the material. This determines if the bar will collapse, not merely the axial force.

### 4. Reaction forces

Even though we remove constrained DOFs when solving, we can recover reaction forces at supports.

Plug the full displacement vector back into:

$$F = Ku$$

The entries corresponding to fixed DOFs give the reaction forces.

- NumPy provides convenient operations for yielding reduced matrices and reconstructing the full displacement vector.
