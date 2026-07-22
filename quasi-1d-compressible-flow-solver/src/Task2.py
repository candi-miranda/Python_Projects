"""
Task 2 – Transient Blowdown Solver
Aerodynamics III HW#1 2025/26
"""

import numpy as np


def _euler_step(P01, P02, mdot, R, T0, V, dt):
    """
    Advance reservoir pressures by one explicit Euler step.

    From ideal gas (isothermal, fixed V):  dP0/dt = (R·T0/V)·(dm/dt)
    Mass balance:  dm1/dt = -mdot,  dm2/dt = +mdot
    -->  P01(t+dt) = P01(t) - (R·T0/V)·mdot·dt
         P02(t+dt) = P02(t) + (R·T0/V)·mdot·dt
    """
    coeff   = (R * T0 / V) * dt
    P01_new = P01 - coeff * mdot
    P02_new = P02 + coeff * mdot
    return P01_new, P02_new


def _adaptive_dt(P01, P02, mdot, R, T0, V, alpha=0.02, dt_max=1.0):
    """
    Compute an adaptive time step that limits each step to a fraction alpha
    of the current pressure difference, keeping the quasi-steady assumption valid.

        dt = alpha · (P01 - P02) / (R·T0/V · mdot)

    Capped at dt_max to avoid large jumps near equilibrium.
    """
    if mdot <= 0.0:
        return dt_max
    rate = (R * T0 / V) * mdot
    return min(alpha * (P01 - P02) / rate, dt_max)


def run_transient(
    gamma, R, T0, V,
    P01_init, P02_init,
    A_throat, A_pipe, L, q_rate,
    solve_steady_state,
    dt_fixed=None,
    alpha=0.02,
    dt_max=1.0,
    tol_mach=0.01,
    t_max=1e6,
    store_spatial_every=200,
    **ss_kwargs,
):
    """
    Explicit Euler blowdown integration from P01_init until equilibrium.

    Parameters
    ----------
    gamma, R, T0       : gas properties and shared stagnation temperature
    V                  : reservoir volume [m³] (both reservoirs equal)
    P01_init, P02_init : initial stagnation pressures [Pa]
    A_throat, A_pipe, L: throat area, pipe area, pipe length
    q_rate             : heat per unit pipe length [W/m]
    solve_steady_state : Task 1 solver function
    dt_fixed           : fixed time step [s]; None → adaptive
    alpha              : adaptive dt safety factor (~0.01–0.05)
    dt_max             : maximum allowed time step [s]
    tol_mach           : stop when max Mach across all stations < tol_mach
    t_max              : hard time limit [s]
    store_spatial_every: save full spatial snapshot every N steps
    **ss_kwargs        : extra keyword args forwarded to solve_steady_state
                         (e.g. profile='sinusoidal')

    Returns
    -------
    dict with keys: t, P01, P02, mdot, station_M, station_T, station_P,
                    spatial_snapshots
    """
    P01, P02 = float(P01_init), float(P02_init)
    t, step  = 0.0, 0

    t_hist    = [t]
    P01_hist  = [P01]
    P02_hist  = [P02]
    mdot_hist = []

    # Merged station: nozzle_out and pipe_in are the same physical location
    station_keys = ['nozzle_in', 'throat', 'nozzle_out/pipe_in', 'pipe_out']
    station_M = {k: [] for k in station_keys}
    station_T = {k: [] for k in station_keys}
    station_P = {k: [] for k in station_keys}
    spatial_snapshots = []

    while True:
        # Guard: if pressures have crossed (overshoot from large dt), stop immediately
        if P02 >= P01:
            print(f"[Task2] Flow stopped at t={t:.3f}s "
                  f"(P01={P01/1e3:.2f} kPa, P02={P02/1e3:.2f} kPa)")
            break

        # Call Task 1 with current pressures — always full regime detection for correctness
        result = solve_steady_state(
            gamma=gamma, R=R,
            P01=P01, P02=P02,
            T0=T0,
            A_throat=A_throat, A_pipe=A_pipe,
            L=L, q_rate=q_rate,
            num_spatial=50,   # coarser grid for speed; Task1 GUI uses full 1000
            **ss_kwargs,      # forward profile= and any other kwargs from GUI
        )
        mdot = result['mdot']

        stations = result.get('stations', {})
        # Map merged station to the nozzle_out index (= pipe_in - 1, same x location)
        station_idx_map = {
            'nozzle_in':          stations.get('nozzle_in'),
            'throat':             stations.get('throat'),
            'nozzle_out/pipe_in': stations.get('nozzle_out'),
            'pipe_out':           stations.get('pipe_out'),
        }
        for k in station_keys:
            idx = station_idx_map.get(k)
            if idx is not None:
                station_M[k].append(result['M'][idx])
                station_T[k].append(result['T'][idx])
                # For nozzle_out/pipe_in in shock regime, compute P analytically
                # from P_stg_in and subsonic area ratio to avoid discrete-grid wobble
                if k == 'nozzle_out/pipe_in' and result['regime'] == 'shock':
                    P_stg  = result['P_stg_in']
                    M_no   = result['M'][idx]
                    P_anal = P_stg * (1 + 0.5*(gamma-1)*M_no**2)**(- gamma/(gamma-1))
                    station_P[k].append(P_anal)
                else:
                    station_P[k].append(result['P'][idx])
            else:
                station_M[k].append(np.nan)
                station_T[k].append(np.nan)
                station_P[k].append(np.nan)

        mdot_hist.append(mdot)

        if step % store_spatial_every == 0:
            spatial_snapshots.append((t, result))

        # End condition: mdot gone (P02>=P01 is caught at top of loop after Euler step)
        if mdot <= 0.0:
            print(f"[Task2] Flow stopped at t={t:.3f}s "
                  f"(P01={P01/1e3:.2f} kPa, P02={P02/1e3:.2f} kPa)")
            break

        # Time step
        dt = float(dt_fixed) if dt_fixed is not None else \
             _adaptive_dt(P01, P02, mdot, R, T0, V, alpha, dt_max)

        P01, P02 = _euler_step(P01, P02, mdot, R, T0, V, dt)
        t    += dt
        step += 1

        t_hist.append(t)
        P01_hist.append(P01)
        P02_hist.append(P02)

        # Mach-based convergence: stop when all stations are below tol_mach
        mach_vals = [station_M[k][-1] for k in station_keys
                     if station_M[k] and not np.isnan(station_M[k][-1])]
        max_mach = max(mach_vals) if mach_vals else 1.0
        if max_mach < tol_mach:
            print(f"[Task2] Converged at t={t:.3f}s")
            break

        if t >= t_max:
            print(f"[Task2] Warning: reached t_max={t_max}s without convergence.")
            break

    # Pad so all arrays align with t_hist
    mdot_hist.append(0.0)
    for k in station_keys:
        station_M[k].append(np.nan)
        station_T[k].append(np.nan)
        station_P[k].append(np.nan)

    return {
        't':      np.array(t_hist),
        'P01':    np.array(P01_hist),
        'P02':    np.array(P02_hist),
        'mdot':   np.array(mdot_hist),
        'station_M': {k: np.array(v) for k, v in station_M.items()},
        'station_T': {k: np.array(v) for k, v in station_T.items()},
        'station_P': {k: np.array(v) for k, v in station_P.items()},
        'spatial_snapshots': spatial_snapshots,
    }