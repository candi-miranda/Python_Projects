# Aerostructural Design Optimization — ATR 72-600

**Aircraft Optimal Design (MEAer) — Final Project, 2025/26**

Conceptual aerostructural design study of the ATR 72-600 regional turboprop, built with [OpenAeroStruct](https://mdolab-openaerostruct.readthedocs-hosted.com/) on top of the [OpenMDAO](https://openmdao.org/) multidisciplinary optimization platform. A gradient-based optimizer (SLSQP) sizes the main wing and horizontal tail simultaneously, coupling a Vortex-Lattice Method (VLM) aerodynamic model with a 6-DOF spatial-beam (wingbox) FEM structural model, to maximize cruise range (Breguet equation) subject to trim and structural failure constraints.

Full methodology, results, and discussion are in [`report_116488_106600_116577_119211.pdf`](./report_116488_106600_116577_119211.pdf). The assignment brief is in [`AOD_HW4.pdf`](./AOD_HW4.pdf).

## Project structure

The optimization was developed progressively, in phases of increasing complexity:

| File | Description |
|---|---|
| `src/baseline_simulation.py` | Baseline (un-optimized) trim-only run — establishes the reference state |
| `src/structural1a_simulation.py` | Phase 1A — wing-only structural optimization (spar/skin thickness) |
| `src/structural1b_simulation.py` | Phase 1B — full structural optimization (wing + tail) |
| `src/aerodynamic_simulation.py` | Aerodynamic/planform optimization (span, sweep, twist) with structure fixed |
| `src/Aerostructural_optimization.py` | Full coupled aerostructural optimization (all design variables simultaneously) |
| `src/Computational_evolution.py` | Reads the SQLite recorder database (`aerostruct.db`) and plots optimization history (range, trim, twist, thickness, constraints) |
| `src/mesh_study.py` | Chordwise mesh refinement / convergence study |

> **Note:** `mesh_study.py` imports a `Range` component from a `range_explicit.py` module that is not included in this repository (it was not recovered from the original project files). This script will raise a `ModuleNotFoundError` if run as-is — it's kept here for reference on the mesh convergence methodology described in the report, not as a runnable script.

## Key results

- Baseline configuration failed to converge (wing structural failure at 86% over yield during the 2.5g maneuver)
- Progressive optimization (structural → aerodynamic → fully coupled aerostructural) improved range from ~1624 km (baseline) to **4911.54 km** (fully coupled optimum)
- The coupled aerostructural optimum favored a **shorter wing span** (20 m vs. the aerodynamics-only optimum of 28.5 m) — a smaller span increases induced drag but sharply cuts root bending moments, letting the structure shed enough mass to more than compensate in the Breguet range equation

## Stack

`numpy` · `openmdao` · `openaerostruct` · `matplotlib` · `scipy` (SLSQP optimizer)

## How to run

```bash
pip install numpy openmdao openaerostruct matplotlib
python src/baseline_simulation.py
python src/structural1a_simulation.py
python src/structural1b_simulation.py
python src/aerodynamic_simulation.py
python src/Aerostructural_optimization.py   # generates aerostruct.db
python src/Computational_evolution.py        # reads aerostruct.db, plots history
```

Run `Aerostructural_optimization.py` before `Computational_evolution.py`, since the latter reads the SQLite recorder file (`aerostruct.db`) produced by the former.
