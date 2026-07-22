# Quasi-1D Compressible Flow Solver
**Aerodynamics III — HW#1 2025/26**

Steady-state and transient blowdown solver for a converging-diverging nozzle coupled to a constant-area Rayleigh pipe.

---

## Files

| File | Description |
|---|---|
| `Task1.py` | Steady-state quasi-1D solver (isentropic nozzle + Rayleigh pipe) |
| `Task2.py` | Transient blowdown integrator (explicit Euler, quasi-steady assumption) |
| `GUI.py` | Tkinter GUI — runs both tasks and plots results |

All three files must be in the **same folder**.

---

## Requirements

Python 3.10 or later, with the following packages:

```
numpy
scipy
matplotlib
```

`tkinter` is part of the Python standard library. If it is missing (some Linux distributions omit it), install it with:

```bash
# Debian/Ubuntu
sudo apt install python3-tk
```

Install the other dependencies with:

```bash
pip install numpy scipy matplotlib
```

---

## How to Run

Launch the GUI from the terminal inside the project folder:

```bash
python GUI.py
```

A window will open with an input panel on the left and a plot area on the right.

---

## Using the GUI

### Input parameters

| Parameter | Description |
|---|---|
| γ | Specific heat ratio |
| R (J/kg·K) | Specific gas constant |
| P₀,₁ (Pa) | Upstream stagnation pressure |
| P₀,₂ (Pa) | Downstream back pressure |
| T₀ (K) | Stagnation temperature (shared) |
| A_throat (m²) | Nozzle throat area |
| A_pipe (m²) | Pipe cross-sectional area (must be > A_throat) |
| L (m) | Pipe length (nozzle length equals pipe length) |
| q' (W/m) | Heat input per unit pipe length (negative = cooling) |
| V (m³) | Reservoir volume — Task 2 only |

A set of **preset cases** is available in the dropdown at the top of the input panel, covering subsonic, supersonic, shock, and Rayleigh heating/cooling scenarios for both tasks.

### Nozzle profile

Choose between **Sinusoidal** and **Polinomial** (quadratic) contours for the converging-diverging nozzle.

### Task 1 — Steady-State

Click **Executar Tarefa 1 (Steady)**. The solver detects the flow regime automatically and plots:

- Mach number, static pressure, stagnation pressure
- Static temperature, stagnation temperature, entropy change
- Mass flow rate, nozzle geometry

The blue status bar at the bottom of the input panel reports the mass flow rate, detected regime, normal shock location (if present), and a warning if the pipe flow is thermally choked.

### Task 2 — Transient Blowdown

Click **Executar Tarefa 2 (Transient)**. The solver integrates forward in time using the quasi-steady assumption (each time step calls the Task 1 solver with the current reservoir pressures) until the pressures equalise. Plots shown are reservoir pressures, mass flow rate, and Mach/temperature/pressure histories at four stations.

**Timestep options:**

- **Variável** — adaptive step size (recommended); controlled internally by the solver
- **Input do Utilizador** — fixed step size in seconds; enter the value in the field below

The estimated run time is shown in the status bar before the simulation starts. Task 2 runs in a background thread so the GUI stays responsive.

---

## Flow Regimes (Task 1)

The solver automatically identifies one of the following regimes:

| Regime | Description |
|---|---|
| `subsonic` | Nozzle is unchoked; fully subsonic flow throughout |
| `shock` | Normal shock inside the nozzle diverging section |
| `supersonic` | Fully supersonic nozzle and pipe; back pressure matched by expansion |

If the pipe flow is supersonic and the total heat addition is large enough to drive the stagnation temperature to the Rayleigh critical value before the pipe exit, the status bar will display **⚠ thermal choking in pipe**. The steady-state solver does not resolve the resulting pipe shock, but the flag is raised as a warning.