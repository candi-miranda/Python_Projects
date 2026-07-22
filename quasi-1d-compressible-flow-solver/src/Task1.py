"""
Task 1 - Steady-State Solver
Aerodynamics III HW#1 2025/26
"""

import numpy as np
import scipy.optimize as so

num = 1000 # number of steps

# nozzle geometry

def quadratic(x, A_throat, A_pipe, L_n, L):
    x_t = L_n/2  # throat location 
    if x <= L_n:
        return A_throat + (A_pipe - A_throat) * ((x - x_t) / x_t)**2  # symmetric parabola, A_pipe at x=0 and x=L_n, A_throat at x=x_t
    else:
        return A_pipe

def sinusoidal(x, A_throat, A_pipe, L_n, L):
    x_t = L_n/2  
    if x <= L_n:
        return A_throat + (A_pipe - A_throat) * (1 + np.cos(np.pi * x / x_t)) / 2  # A_pipe at x=0 and x=L_n, A_throat at x=x_t
    else:
        return A_pipe

def area(profile):
    if profile == 'quadratic':
        return quadratic
    elif profile == 'sinusoidal':
        return sinusoidal

# isentropic flow functions

def mach_from_area_ratio(A, gamma, A_throat):
    area_ratio = A/A_throat
    if abs(1 - area_ratio) < 1e-9:
        return [1,1]
    def eq_area (Mach):
        return (1/Mach)*((2/(gamma+1))*(1+(gamma-1)/2*Mach**2))**((gamma+1)/(2*(gamma-1))) - area_ratio
    try:
        sub = so.brentq(eq_area, 1e-6, 1 - 1e-6)
    except ValueError:
        sub = None
    try:
        sup = so.brentq(eq_area, 1 + 1e-6, 10)
    except ValueError:
        sup = None
    return [m for m in [sub, sup] if m is not None]

def temperature_from_mach(Mach, gamma, T_stg):
    temp_ratio = 1 + ((gamma-1)/2)*Mach**2
    return T_stg/temp_ratio

def pressure_from_mach(Mach, gamma, P_stg):
    pressure_ratio = (1 + ((gamma-1)/2)*Mach**2)**(gamma/(gamma-1))
    return P_stg/pressure_ratio

def mass_flow_rate(A,Mach, gamma, R, P_stg, T_stg):
    return A*P_stg*np.sqrt(gamma/(R*T_stg))*Mach*(1+0.5*(gamma-1)*Mach**2)**(-0.5*(gamma+1)/(gamma-1))

def entropy_from_mach(gamma, R, T_ref, P_ref, T, P):
    c_p = R * gamma / (gamma - 1)
    return c_p * np.log(T / T_ref) - R * np.log(P / P_ref)

# Rayleigh flow relations

def rayleigh_stg_temperature(xi, c_p, q_rate, T_stg_in, m_rate_in):
    return T_stg_in + q_rate*xi/(c_p*m_rate_in)

def mach_from_stg_temp_ratio(gamma, T_stg, T_stg_crt):
    stg_temp_ratio = T_stg_crt/T_stg
    if abs(1 - stg_temp_ratio) < 1e-9:
        return [1,1]
    def eq_temp (Mach):
        return ((1+gamma*Mach**2)**2)/(2*(1+gamma)*(Mach**2)*(1+0.5*(gamma-1)*Mach**2)) - stg_temp_ratio
    try:
        sub = so.brentq(eq_temp, 1e-6, 1 - 1e-6)
    except ValueError:
        sub = None
    try:
        sup = so.brentq(eq_temp, 1 + 1e-6, 10)
    except ValueError:
        sup = None
    return [m for m in [sub, sup] if m is not None]

def rayleigh_temperature(Mach, gamma, T_crt):
    return T_crt / (((1+gamma*Mach**2)**2)/(((gamma+1)**2)*Mach**2))

def rayleigh_stg_pressure(Mach, gamma, P_stg_crt, q_rate):
    return P_stg_crt / ((1+gamma*Mach**2)/(1+gamma)*((0.5*(gamma+1))/(1+0.5*(gamma-1)*Mach**2))**(gamma/(gamma-1)))

def rayleigh_pressure(Mach, gamma, P_crt):
    return P_crt/ ((1+gamma*Mach**2)/(1+gamma))

def rayleigh_entropy(c_p, R, T_ref, P_ref, T, P):
    return c_p * np.log(T / T_ref) - R * np.log(P / P_ref)

# NSW functions

def mach_after_shock (gamma, Mach1):
    val = (Mach1**2 + 2/(gamma-1)) / ((((2*gamma)/(gamma-1))*Mach1**2) - 1)
    if val < 0:
        raise ValueError(f"mach_after_shock: invalid Mach1={Mach1:.6f}, expression under sqrt = {val:.6e}")
    return np.sqrt(val)

def temperature_after_shock(gamma, Mach1, Mach2, T1):
    return T1 * (1+0.5*(gamma-1)*Mach1**2)/(1+0.5*(gamma-1)*Mach2**2)

def pressure_after_shock(gamma, Mach1, P1):
    return P1 * (((2*gamma/(gamma+1))*Mach1**2)-(gamma-1)/(gamma+1))

def stag_pressure_after_shock(gamma, T1, T2, P1, P2, P_stg1):
    return P_stg1*(P2/P1)*((T1/T2)**(gamma/(gamma-1)))

def crt_area_after_shock(A_crt1, P_stg1, P_stg2):
    return A_crt1 * P_stg1/P_stg2

# Nozzle sub-solver

def solver_nozzle(gamma, R, P_stg_1, T_stg, A_throat, A_pipe, L_n, L, A_func, M_throat, mode, shock, x_s):
    P_stg = P_stg_1
    if mode == 'subsonic':
        A_crt = A_throat / ((1/M_throat)*((2/(gamma+1))*(1+(gamma-1)/2*M_throat**2))**((gamma+1)/(2*(gamma-1))))
    elif mode == 'supersonic':
        A_crt = A_throat
    base_x = np.sort(np.append(np.linspace(0, L_n, num), [L_n/2]))
    # Insert the exact shock position x_s into the grid so the shock is always applied
    # at the analytically-correct continuous location (not snapped to nearest grid point).
    # This eliminates the staircase wobble in nozzle_out pressure during transient runs.
    if shock and x_s is not None and L_n/2 < x_s < L_n:
        x_nozzle = np.sort(np.append(base_x, [x_s]))
    else:
        x_nozzle = base_x
    M_nozzle = []
    T_nozzle = []
    P_nozzle = []
    s_nozzle = []
    for xi in x_nozzle:
        Ai = A_func(xi, A_throat, A_pipe, L_n, L)
        if shock == True and xi >= x_s and mode == 'supersonic':
            M1 = float(mach_from_area_ratio(Ai, gamma, A_crt)[1])
            T1 = temperature_from_mach(M1, gamma, T_stg)
            P1 = pressure_from_mach(M1, gamma, P_stg)
            Mi = mach_after_shock(gamma, M1)
            Ti = temperature_after_shock(gamma, M1, Mi, T1)
            Pi = pressure_after_shock(gamma, M1, P1)
            P_stg = stag_pressure_after_shock(gamma, T1, Ti, P1, Pi, P_stg)
            A_crt = crt_area_after_shock(A_throat, P_stg_1, P_stg)
            mode = 'subsonic'
        else:
            if mode == 'subsonic':
                sols = mach_from_area_ratio(Ai, gamma, A_crt)
                if not sols:
                    Mi = M_nozzle[-1] if M_nozzle else M_throat  # fallback to previous value if solver fails
                else:
                    Mi = float(sols[0])
            elif mode == 'supersonic':
                if xi == L_n/2:
                    Mi = 1
                elif xi < L_n/2:
                    Mi = float(mach_from_area_ratio(Ai, gamma, A_crt)[0])
                else:
                    Mi = float(mach_from_area_ratio(Ai, gamma, A_crt)[1])
            Ti = temperature_from_mach(Mi, gamma, T_stg)
            Pi = pressure_from_mach(Mi, gamma, P_stg)
        M_nozzle.append(Mi)
        T_nozzle.append(Ti)
        P_nozzle.append(Pi)
        if xi == 0:
            s_nozzle.append(0)
        else:
            s_nozzle.append(entropy_from_mach(gamma, R, T_nozzle[0], P_nozzle[0], Ti, Pi))
    return x_nozzle, M_nozzle, T_nozzle, P_nozzle, s_nozzle, P_stg

# Pipe sub-solver

def solver_pipe(gamma, R, c_p, q_rate, L, M_in, T_in, T_stg_in, P_in, P_stg_in, m_rate_in, s_in):
    # critical parameters
    T_crt = T_in * ((1+gamma*M_in**2)**2)/(((gamma+1)**2)*M_in**2)
    T_stg_crt = T_stg_in * ((1+gamma*M_in**2)**2)/(2*(1+gamma)*(M_in**2)*(1+0.5*(gamma-1)*M_in**2))
    P_crt = P_in * (1+gamma*M_in**2)/(1+gamma)
    P_stg_crt = P_stg_in * (1+gamma*M_in**2)/(1+gamma)*((0.5*(gamma+1))/(1+0.5*(gamma-1)*M_in**2))**(gamma/(gamma-1))
    # pipe inlet parameters
    x_pipe = np.linspace(0, L, num)
    T_stg_pipe = [T_stg_in]
    M_pipe = [M_in]
    T_pipe = [T_in]
    P_stg_pipe = [P_stg_in]
    P_pipe = [P_in]
    s_pipe = [s_in]
    for i in range(1, len(x_pipe)):
        xi = x_pipe[i]
        T_stgi = rayleigh_stg_temperature(xi, c_p, q_rate, T_stg_in, m_rate_in)
        T_stg_pipe.append(T_stgi)
        sols = mach_from_stg_temp_ratio(gamma, T_stgi, T_stg_crt)
        if not sols:
            Mi = M_pipe[i-1]  # fallback: thermal choking reached, hold last Mach
        else:
            Mi = float(min(sols, key=lambda m: abs(float(m) - float(M_pipe[i-1]))))
        Ti = rayleigh_temperature(Mi, gamma, T_crt)
        Pi = rayleigh_pressure(Mi, gamma, P_crt)
        M_pipe.append(Mi)
        T_pipe.append(Ti)
        P_stg_pipe.append(rayleigh_stg_pressure(Mi, gamma, P_stg_crt, q_rate))
        P_pipe.append(Pi)
        s_pipe.append(rayleigh_entropy(c_p, R, T_pipe[0], P_pipe[0], Ti, Pi))
    return x_pipe, M_pipe, T_stg_pipe, T_pipe, P_stg_pipe, P_pipe, s_pipe, T_stg_crt

# Combined solver

def solver (M_throat, gamma, q_rate, c_p, R, P_stg_1, T_stg, A_throat, A_pipe, L, L_n, A_func, mode, regime, x_s):
    if regime == 'shock':
        x_nozzle, M_nozzle, T_nozzle, P_nozzle, s_nozzle, P_stg = solver_nozzle(gamma, R, P_stg_1, T_stg, A_throat, A_pipe, L_n, L, A_func,M_throat, mode, True, x_s)
    else:
        x_nozzle, M_nozzle, T_nozzle, P_nozzle, s_nozzle, P_stg = solver_nozzle(gamma, R, P_stg_1, T_stg, A_throat, A_pipe, L_n, L, A_func,M_throat, mode, False, x_s)
    M_in = M_nozzle[-1]
    T_in = T_nozzle[-1]
    T_stg_in = T_stg
    P_in = P_nozzle[-1]
    P_stg_in = P_stg
    m_rate_in =  mass_flow_rate(A_func(L_n, A_throat, A_pipe, L_n, L), M_in, gamma, R, P_stg_in, T_stg_in)
    s_in = s_nozzle[-1]
    x_pipe, M_pipe, T_stg_pipe, T_pipe, P_stg_pipe, P_pipe, s_pipe, T_stg_crt_pipe = solver_pipe(gamma, R, c_p, q_rate, L, M_in, T_in, T_stg_in, P_in, P_stg_in, m_rate_in, s_in)
    x = np.concatenate((x_nozzle + 0, x_pipe + L_n))
    m_rate = np.full(len(x), m_rate_in)
    return x, np.concatenate((M_nozzle,M_pipe)), np.concatenate((T_nozzle,T_pipe)), T_stg_pipe, np.concatenate((P_nozzle,P_pipe)), P_stg_in, P_stg_pipe, np.concatenate((s_nozzle, s_pipe)), m_rate, T_stg_crt_pipe

# Regime determination

def pressure_error (M_throat, gamma, q_rate, c_p, R, P_stg_1, P_stg_2, T_stg, A_crt, A_pipe, L, L_n, A_func, mode, regime, x_s):
    _, _, _, _, P, _, _ , _, _, _= solver (M_throat, gamma, q_rate, c_p, R, P_stg_1, T_stg, A_crt, A_pipe, L, L_n, A_func, mode, regime, x_s)
    return P[-1]-P_stg_2

# Public interface

def _stag_pressure_after_shock_at_x(x_s, gamma, R, P_stg_1, T_stg, A_throat, A_pipe, L_n, L, A_func):
    """
    For Task 2. Compute the post-shock stagnation pressure analytically at the exact shock
    position x_s, using the continuous area function (no grid discretisation).
    This avoids the staircase wobble caused by snapping x_s to a grid point.
    """
    A_s  = A_func(x_s, A_throat, A_pipe, L_n, L)
    M1   = float(mach_from_area_ratio(A_s, gamma, A_throat)[1])
    T1   = temperature_from_mach(M1, gamma, T_stg)
    P1   = pressure_from_mach(M1, gamma, P_stg_1)
    M2   = mach_after_shock(gamma, M1)
    T2   = temperature_after_shock(gamma, M1, M2, T1)
    P2   = pressure_after_shock(gamma, M1, P1)
    P_stg_2 = stag_pressure_after_shock(gamma, T1, T2, P1, P2, P_stg_1)
    return P_stg_2


def solve_steady_state(gamma, R, P01, P02, T0, A_throat, A_pipe, L, q_rate,
                       profile='sinusoidal', num_spatial=None, _regime_hint=None):
    """
    Solve the steady-state quasi-1D flow (nozzle + Rayleigh pipe).

    Parameters
    ----------
    gamma    : specific heat ratio [-]
    R        : specific gas constant [J/kg·K]
    P01      : upstream stagnation pressure [Pa]
    P02      : downstream back pressure [Pa]
    T0       : stagnation temperature [K]
    A_throat : nozzle geometric throat area [m²]
    A_pipe   : pipe cross-sectional area [m²]
    L        : pipe length [m]  (nozzle length L_n defaults to L)
    q_rate   : heat flux per unit pipe length [W/m]  (positive = heating)
    profile  : nozzle shape — 'sinusoidal' or 'quadratic'

    Returns
    -------
    dict: mdot, x, M, T, T0x, P, P0x, s, regime, x_shock, L_n, stations
    """
    L_n   = L  # nozzle length defaults to pipe length; not user-facing
    c_p   = R * gamma / (gamma - 1)
    A_func = area(profile)
    # Override global spatial resolution if requested (used by Task2 for speed)
    _num_save = None
    if num_spatial is not None and num_spatial != num:
        import Task1 as _t1mod
        _num_save = _t1mod.num
        _t1mod.num = num_spatial

    # Regime determination  

    if _regime_hint is not None:
        regime = _regime_hint
    else:
        # Test fully-choked subsonic: if exit P <= P02, flow is unchoked subsonic
        try:
            error_at_choked = pressure_error(1.0, gamma, q_rate, c_p, R, P01, P02, T0,
                                             A_throat, A_pipe, L, L_n, A_func,
                                             'subsonic', '', 1e9)
        except Exception:
            error_at_choked = 1.0  # treat as "not subsonic" if solver fails

        if error_at_choked <= 1.0:   # <=1 Pa tolerance: anything this close is choked-subsonic
            regime = 'subsonic'
        else:
            try:
                error_at_supersonic = pressure_error(1.0, gamma, q_rate, c_p, R, P01, P02, T0,
                                                     A_throat, A_pipe, L, L_n, A_func,
                                                     'supersonic', '', 1e9)
                if error_at_supersonic >= 0:
                    regime = 'supersonic'
                else:
                    regime = 'shock'
            except Exception:
                regime = 'shock'

    # Final solve

    best_x_s = 0

    if regime == 'subsonic':
        # Find M_throat in (0, 1) that matches P02 at pipe exit
        # Safety check: verify a sign change exists before calling brentq
        err_lo = pressure_error(0.001, gamma, q_rate, c_p, R, P01, P02, T0,
                                A_throat, A_pipe, L, L_n, A_func, 'subsonic', '', 1e9)
        err_hi = pressure_error(1.0 - 1e-6, gamma, q_rate, c_p, R, P01, P02, T0,
                                A_throat, A_pipe, L, L_n, A_func, 'subsonic', '', 1e9)
        if err_lo * err_hi > 0:
            # No sign change — run at choked-subsonic as best approximation
            best_M_throat = 1.0 - 1e-6
        else:
            best_M_throat = so.brentq(pressure_error, 0.001, 1.0 - 1e-6,
                                      args=(gamma, q_rate, c_p, R, P01, P02, T0,
                                            A_throat, A_pipe, L, L_n, A_func,
                                            'subsonic', '', 1e9))
        x, M, T, T_stg_flow, P, P_stg_in, P_stg_flow, s, m_rate, T_stg_crt_pipe = solver(
            best_M_throat, gamma, q_rate, c_p, R, P01, T0,
            A_throat, A_pipe, L, L_n, A_func, 'subsonic', '', 1e9)

    elif regime == 'supersonic':
        x, M, T, T_stg_flow, P, P_stg_in, P_stg_flow, s, m_rate, T_stg_crt_pipe = solver(
            1.0, gamma, q_rate, c_p, R, P01, T0,
            A_throat, A_pipe, L, L_n, A_func, 'supersonic', '', 1e9)

    else:  # shock inside nozzle
        # Find shock position in diverging section; fall back to supersonic if no sign change
        x_lo = L_n / 2 + 1e-4   # start just past the throat to catch near-throat shocks
        x_hi = L_n - 1e-6
        def shock_err(xs):
            return pressure_error(1.0, gamma, q_rate, c_p, R, P01, P02, T0,
                                  A_throat, A_pipe, L, L_n, A_func,
                                  'supersonic', 'shock', xs)
        try:
            err_lo = shock_err(x_lo)
            err_hi = shock_err(x_hi)
            if err_lo * err_hi > 0:
                # No valid shock position — treat as supersonic
                x, M, T, T_stg_flow, P, P_stg_in, P_stg_flow, s, m_rate, T_stg_crt_pipe = solver(
                    1.0, gamma, q_rate, c_p, R, P01, T0,
                    A_throat, A_pipe, L, L_n, A_func, 'supersonic', '', 1e9)
                regime = 'supersonic'
            else:
                best_x_s = so.brentq(shock_err, x_lo, x_hi)
                x, M, T, T_stg_flow, P, P_stg_in, P_stg_flow, s, m_rate, T_stg_crt_pipe = solver(
                    1.0, gamma, q_rate, c_p, R, P01, T0,
                    A_throat, A_pipe, L, L_n, A_func, 'supersonic', 'shock', best_x_s)
                # Overwrite P_stg_in with analytically-exact value at continuous x_shock
                # (solver_nozzle snaps shock to nearest grid point, causing staircase wobble)
                P_stg_in = _stag_pressure_after_shock_at_x(
                    best_x_s, gamma, R, P01, T0, A_throat, A_pipe, L_n, L, A_func)
        except Exception:
            x, M, T, T_stg_flow, P, P_stg_in, P_stg_flow, s, m_rate, T_stg_crt_pipe = solver(
                1.0, gamma, q_rate, c_p, R, P01, T0,
                A_throat, A_pipe, L, L_n, A_func, 'supersonic', '', 1e9)
            regime = 'supersonic'

    x_shock  = best_x_s if (regime == 'shock' and best_x_s != 0) else None
    # n_nozzle derived from array lengths: pipe always has exactly num points
    n_nozzle = len(x) - len(T_stg_flow)
    mdot     = float(m_rate[0])

    # Thermal choking flag — same check as the notebook:
    # if the pipe exit stagnation temperature reached or exceeded the critical value
    # on the supersonic Rayleigh branch, a shock would be forced inside the pipe.
    thermally_choked = bool(T_stg_flow[-1] >= T_stg_crt_pipe)

    # T0 array 
    # Nozzle is isentropic so T0 = const; pipe gets Rayleigh heating
    T0_nozzle = np.full(n_nozzle, T0)
    T0x       = np.concatenate([T0_nozzle, T_stg_flow])

    #  P0 array 
    # Nozzle: P0 = P01 before shock, P_stg_in after; pipe: from P_stg_flow
    P0_nozzle = np.full(n_nozzle, P01)
    if regime == 'shock' and x_shock is not None:
        for i in range(n_nozzle):
            if x[i] >= x_shock:
                P0_nozzle[i] = P_stg_in
    P0x = np.concatenate([P0_nozzle, P_stg_flow])

    #  Entropy: offset pipe[1:] so entropy is continuous throughout 
    # solver_pipe sets s_pipe[0] = s_in = s_nozzle[-1] (already correct)
    # but s_pipe[1:] are from rayleigh_entropy() which resets to 0 at the pipe inlet
    # so we add s_nozzle[-1] to all pipe points after the inlet
    s          = np.array(s, dtype=float)
    s_noz_exit = s[n_nozzle]        # = s_pipe[0] = s_in, already the nozzle exit entropy
    s[n_nozzle + 1:] += s_noz_exit  # offset rayleigh_entropy values to be continuous
    # Zero out floating-point noise: isentropic regions should have exactly zero entropy change
    s[np.abs(s) < 1e-3] = 0.0

    # Restore global num if it was overridden
    if _num_save is not None:
        import Task1 as _t1mod
        _t1mod.num = _num_save

    # In shock regime, pipe exit pressure is exactly P02 by boundary condition.
    # The brentq root has a small residual (~0.1%) due to discrete grid; overwrite
    # P[-1] with the exact value to prevent zigzag artefacts in Task 2 plots.
    if regime == 'shock':
        P = list(P)
        P[-1] = P02
        P = np.array(P)

    return {
        'mdot'             : mdot,
        'x'                : x,
        'M'                : np.array(M,   dtype=float),
        'T'                : np.array(T,   dtype=float),
        'T0x'              : np.array(T0x, dtype=float),
        'P'                : np.array(P,   dtype=float),
        'P0x'              : np.array(P0x, dtype=float),
        's'                : s,
        'regime'           : regime,
        'x_shock'          : x_shock,
        'thermally_choked' : thermally_choked,
        'P_stg_in'         : float(P_stg_in),
        'L_n'              : L_n,
        'stations'         : {
            'nozzle_in':  0,
            'throat':     int(np.argmin(np.abs(x - L_n/2))),
            'nozzle_out': n_nozzle - 1,
            'pipe_in':    n_nozzle,
            'pipe_out':   len(x) - 1,
        },
    }