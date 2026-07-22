# Aircraft Optimal Design — Homework 3

Code for the 3rd assignment of the **Aircraft Optimal Design** course (MEAer, Instituto
Superior Técnico, 2nd semester 2025/26). The assignment covers constrained optimization
with OpenMDAO and aerodynamic shape optimization of a wing with OpenAeroStruct.

The full assignment statement is available in [`report/assignment_statement.pdf`](report/assignment_statement.pdf).

## Repository structure

```
AOD_HW3/
├── problem1_openmdao_optimization/   # Problem 1: Himmelblau's function in OpenMDAO
├── problem3_aero_optimization/       # Problem 3: wing aerodynamic optimization (OpenAeroStruct)
└── report/                           # Assignment statement (and, once written, the final report PDF)
```

### Problem 1 — Constrained optimization using OpenMDAO

Minimization of Himmelblau's function, `f(x1, x2) = (x1² + x2 − 11)² + (x1 + x2² − 7)²`,
built up incrementally as an OpenMDAO `ExplicitComponent`.

| File | Description |
|---|---|
| `alinea_b.py` | Defines `f(x)` as an OpenMDAO component and generates the N2 diagram (`openmdao n2 alinea_b.py`). |
| `alinea_c.py` | Solves the unconstrained problem from `x0 = (0, 0)` with SLSQP, using finite-difference partials. |
| `alinea_d.py` | Adds the constraint `−x1 − x2 ≤ 0` and profiles the number of function calls / CPU time. |
| `alinea_e.py` | Repeats the constrained optimization using analytic (hand-derived) partial derivatives instead of finite differences, for comparison against `alinea_d.py`. |

### Problem 3 — Aerodynamic optimization using OpenAeroStruct

Optimization of a rectangular Cessna 172-like wing (span 11 m, area 16.2 m², NACA 2412,
cruise at 63 m/s and 2000 m) built on top of the
[OpenAeroStruct aerodynamic walkthrough example](https://mdolab-openaerostruct.readthedocs-hosted.com/en/latest/aero_walkthrough.html).

| Folder | Description |
|---|---|
| `3a_mesh_convergence_study/` | `run_aero.py` runs the baseline VLM aerodynamic analysis; `mesh_study.py` sweeps the spanwise mesh resolution and studies convergence of `CD` and runtime. |
| `3b_i_alpha_only/` | Optimization with the angle of attack `α` as the only design variable. `run_aero3b.py` runs the case, `plot_aero.py` plots the optimization history from the resulting case-recorder database. |
| `3b_ii_alpha_twist/` | Optimization with `α` and the spanwise twist distribution `γ(y)` as design variables. |
| `3b_iii_alpha_chord/` | Optimization with `α` and the spanwise chord distribution `c(y)`, compared across three chord parametrizations: `3b_iii_linear.py`, `3b_iii_quadratic.py`, and `3b_iii_eliptical.py`. `plot_aero.py` overlays the optimization histories of the three cases. |
| `3b_iv_alpha_twist_chord/` | Optimization with all three design variables together: `α`, `γ(y)`, and `c(y)`. |
| `3c_3d_new_constraint/` | `run_aero_3c.py` adds a new aerodynamic-efficiency constraint/objective (custom `AeroEfficiency` component) on top of the Problem 3(b) setup, re-running the optimization with the extra constraint. |

> **Note:** `run_aero_3c.py` imports a custom component `AeroEfficiency` from a local module
> `efficiency_comp.py`. That file was not present among the uploaded scripts — add it to
> `3c_3d_new_constraint/` (or update the import) before running this script.

## Requirements

- Python 3
- [OpenMDAO](https://openmdao.org/)
- [OpenAeroStruct](https://github.com/mdolab/OpenAeroStruct)
- NumPy, Matplotlib

Install following the course notes' appendix, or e.g.:

```bash
pip install openmdao openaerostruct numpy matplotlib
```

## Running the scripts

Each script is self-contained and can be run directly, e.g.:

```bash
cd problem1_openmdao_optimization
python alinea_d.py

cd ../problem3_aero_optimization/3b_i_alpha_only
python run_aero3b.py
python plot_aero.py
```

Most Problem 3 scripts write an OpenMDAO case-recorder database (`.db` file) that the
corresponding `plot_aero.py` reads to plot the optimization history — run the optimization
script first, then the plotting script.

## Author

Cândida — MEAer, Instituto Superior Técnico (IST), supervised by Prof. André C. Marta.

# Aircraft Optimal Design — Final Project (Homework 4)

Code and report for the Final Project of the **Aircraft Optimal Design** course (MEAer,
Instituto Superior Técnico, 2nd semester 2025/26): a conceptual aerostructural design and
optimization of the **ATR 72-600** regional turboprop, using
[OpenAeroStruct](https://github.com/mdolab/OpenAeroStruct) built on top of
[OpenMDAO](https://openmdao.org/).

The full assignment statement is in [`report/assignment_statement.pdf`](report/assignment_statement.pdf)
and the final written report is in [`report/report_116488_106600_116577_119211.pdf`](report/report_116488_106600_116577_119211.pdf).

## Repository structure

```
AOD_HW4/
├── 1_mesh_convergence_study/       # Spanwise/chordwise VLM mesh refinement study
├── 2_baseline/                     # Baseline (un-optimized) trim simulation
├── 3_structural_phase1a_wing_only/ # Structural optimization, wing thicknesses only
├── 4_structural_phase1b_full/      # Structural optimization, wing + tail thicknesses
├── 5_aerodynamic_optimization/     # Aerodynamic/planform optimization (shape fixed structure)
├── 6_aerostructural_optimization/  # Fully coupled aerostructural (MDO) optimization
└── report/                         # Assignment statement + final report PDF
```

Each stage builds on the previous one, following the progression described in the report
(Section 5): baseline → structural (wing-only) → structural (wing + tail) → aerodynamic
shape → full coupled aerostructural MDO.

### 1 — Mesh convergence study (`1_mesh_convergence_study/`)

`mesh_study.py` sweeps the spanwise resolution (`ny`) for a fixed chordwise resolution
(`nx = 21`), running the coupled aerostructural analysis at each resolution and recording
`CL`, `CD` (total/wing/tail), Breguet range, and wall-clock time, then plots `CD` and
runtime vs. `ny` and recommends a converged resolution.

> **Note:** this script imports a custom `Range` component from a local module
> `range_explicit.py`, which was not among the uploaded files. Add
> `range_explicit.py` (an `ExplicitComponent` implementing the Breguet range equation,
> analogous to the `BreguetRange` class used in the other scripts) to this folder before
> running `mesh_study.py`.

### 2 — Baseline (`2_baseline/`)

`baseline_simulation.py` builds the two-point (1g cruise / 2.5g maneuver) aerostructural
model of the ATR 72-600 wing + horizontal tail (wingbox FEM + VLM aerodynamics) with the
geometry and structural thicknesses fixed at their reference values, and only trims the
aircraft (angle of attack at both points, tail twist) to satisfy `L = W` and `CM = 0`. Used
as the reference point against which all later optimizations are compared (Table 7 of the
report).

### 3 — Structural optimization, Phase 1A (`3_structural_phase1a_wing_only/`)

`structural1a_simulation.py` adds the wing spar and skin thickness control points as design
variables (tail structure kept fixed) and maximizes Breguet range subject to the trim and
wing/tail failure constraints, isolating the effect of wing-only structural sizing.

### 4 — Structural optimization, Phase 1B (`4_structural_phase1b_full/`)

`structural1b_simulation.py` extends Phase 1A by also freeing the tail spar and skin
thickness control points, so both lifting surfaces are structurally sized simultaneously.

### 5 — Aerodynamic optimization (`5_aerodynamic_optimization/`)

`aerodynamic_simulation.py` fixes the structural thicknesses (from Phase 1B) and instead
frees the aerodynamic/planform design variables — wing and tail twist, wing sweep, and
wing and tail span — to maximize range through wing shape and platform changes alone.

### 6 — Aerostructural optimization (`6_aerostructural_optimization/`)

`Aerostructural_optimization.py` is the fully coupled MDO run: aerodynamic/planform
variables (twist, span, sweep) and structural variables (spar/skin thickness) are all
freed simultaneously, subject to trim and failure constraints, to jointly maximize Breguet
range. It records the optimization history to `aerostruct.db` and also exports the model
N2 diagram (`n2_aerostrutural.html`).

`Computational_evolution.py` reads `aerostruct.db` (produced by
`Aerostructural_optimization.py`) and plots the optimization history: range, trim angles,
wing/tail twist, wing structural thicknesses, the `L = W` constraints, the pitching-moment
constraint, and the wing/tail failure constraints vs. iteration (Figures 7–8 of the report).

## Requirements

- Python 3
- [OpenMDAO](https://openmdao.org/)
- [OpenAeroStruct](https://github.com/mdolab/OpenAeroStruct)
- NumPy, Matplotlib

```bash
pip install openmdao openaerostruct numpy matplotlib
```

## Running the scripts

Run in order, since later stages reuse thickness/geometry values obtained from earlier
ones (values are hard-coded in each script rather than passed automatically):

```bash
cd 1_mesh_convergence_study && python mesh_study.py   # needs range_explicit.py, see note above
cd ../2_baseline && python baseline_simulation.py
cd ../3_structural_phase1a_wing_only && python structural1a_simulation.py
cd ../4_structural_phase1b_full && python structural1b_simulation.py
cd ../5_aerodynamic_optimization && python aerodynamic_simulation.py
cd ../6_aerostructural_optimization && python Aerostructural_optimization.py
python Computational_evolution.py   # after the aerostructural run, reads aerostruct.db
```

## Reference aircraft

**ATR 72-600** (twin-turboprop regional airliner): span 27.05 m, wing area 61 m², cruise
Mach 0.443 at FL250, MTOW 23 000 kg, OEW ≈ 13 450 kg, aluminum 7075-T6 wingbox structure.
See `report/report_116488_106600_116577_119211.pdf` (Section 2) for the complete list of
baseline parameters and sources.

## Authors

Afonso Vieira, Cândida Miranda, Gonçalo Teixeira, Guilherme Rodrigues — MEAer, Instituto
Superior Técnico (IST), supervised by Prof. André C. Marta.

