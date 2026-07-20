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
