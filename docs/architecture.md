# Architecture


## 1. Purpose
   This is probably the longest document that I'd attached to this project. It presents the overall structure & design of this program for developers who are interested in. By the time you finish reading, you can hopefully get the hang of the entire code & begin adding additional features, upgrades or optimization.
   
### Goals of this document

This document is intended to help readers:

- Understand the overall architecture of the project.
- Build a mental model of how the major subsystems work toghether.
- Navigate the codebase more efficiently.
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

#### FEM Solver
Computes structural displacements, member forces, and stresses from the current model.

#### Evaluation Engine
Interprets solver outputs, evaluates failure criteria, and updates the simulation state during progressive collapse.

#### Renderer
Visualizes the structure, simulation results, and user interface from the evaluation engine.


---


## 4. Core Concepts

### Simulation State

### Nodes

### Elements

### Supports

### External Loads

### Camera

### Selection

### Inspection Mode

---

## 5. Module Architecture

### 5.1 User Interface

Responsibilities

Owns

Uses

Produces

---

### 5.2 Simulation Controller

Responsibilities

Owns

Uses

Produces

---

### 5.3 FEM Solver

Responsibilities

Inputs

Outputs

---

### 5.4 Failure Engine

Responsibilities

Inputs

Outputs

---

### 5.5 Renderer

Responsibilities

Inputs

Outputs

---

## 6. Data Ownership

Which subsystem owns which data?

Mutable vs derived data

---

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
