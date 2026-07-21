import time
import numpy as np
import matplotlib.pyplot as plt
import openmdao.api as om

from openaerostruct.geometry.utils import generate_mesh
from openaerostruct.integration.aerostruct_groups import AerostructGeometry, AerostructPoint
from range_explicit import Range

def mesh_crea(num_y, num_x, span, corda, offset):
    return {
        "num_y": num_y, "num_x": num_x, "wing_type": "rect", "symmetry": True,
        "span_cos_spacing": 1, "span": span, "root_chord": corda, "offset": offset
    }


def run_case(nx, ny, verbose=False):
    # base geometry
    corda = 3.11
    span = 27.05
    Area_main = 61.0
    corda_tail = 1.8845
    span_tail = 8.49

    points_twist = 5
    points_radius = 5
    points_thickness = 5

    # generate meshes
    mesh_dict = mesh_crea(ny, nx, span, corda, [0, 0, 0])
    mesh = generate_mesh(mesh_dict)

    # applies slight camber along the chord
    camber = (1 - np.linspace(-1, 1, nx) ** 2) * corda * 0.04
    for ind_x in range(nx):
        mesh[ind_x, :, 2] = camber[ind_x]

    mesh_dict_tail = mesh_crea(ny, nx, span_tail, corda_tail, [12.0, 0, 0])
    mesh_tail = generate_mesh(mesh_dict_tail)

    name = "main_wing"
    surface = {
        "name": name, "symmetry": True, "S_ref_type": "projected", "fem_model_type": "tube",
        "thickness_cp": 0.05 * np.ones(points_thickness), "radius_cp": 0.5 * np.ones(points_radius),
        "twist_cp": np.zeros(points_twist), "mesh": mesh, "span": span, "sweep": 3.0, "taper": 0.45, "dihedral": 0.0,
        "CL0": 0.0565, "CD0": 0.00715,
        "t_over_c_cp": np.array([0.18]), "c_max_t": 0.30, "with_wave": False, "with_viscous": True, "k_lam": 0.05,
        "E": 71.7e9, "G": 26.9e9, "yield": 505.0e6 / 2.5, "mrho": 2810.0, "fem_origin": 0.30,
        "wing_weight_ratio": 2.0, "struct_weight_relief": True, "distributed_fuel_weight": False, "exact_failure_constraint": False,
    }

    name_tail = "tail_wing"
    surface_tail = {
        "name": name_tail, "symmetry": True, "S_ref_type": "projected", "fem_model_type": "tube",
        "thickness_cp": 0.03 * np.ones(points_thickness), "radius_cp": 0.3 * np.ones(points_radius),
        "twist_cp": np.zeros(points_twist), "mesh": mesh_tail, "span": span_tail, "sweep": 0.0, "taper": 0.5, "dihedral": 0.0,
        "CL0": 0.0, "CD0": 0.00479,
        "t_over_c_cp": np.array([0.09]), "c_max_t": 0.30, "with_wave": False, "with_viscous": True, "k_lam": 0.05,
        "E": 71.7e9, "G": 26.9e9, "yield": 505.0e6 / 2.5, "mrho": 2810.0, "fem_origin": 0.30,
        "wing_weight_ratio": 2.0, "struct_weight_relief": True, "distributed_fuel_weight": False, "exact_failure_constraint": False,
    }

    surfaces = [surface, surface_tail]

    # Sets up the OpenMDAO problem
    prob = om.Problem()

    indep_var_comp = om.IndepVarComp()
    indep_var_comp.add_output("v", val=137.2, units="m/s")
    indep_var_comp.add_output("alpha", val=2.0, units="deg")
    indep_var_comp.add_output("Mach_number", val=0.443)
    indep_var_comp.add_output("re", val=4900000.0, units="1/m")
    indep_var_comp.add_output("rho", val=0.549, units="kg/m**3")
    indep_var_comp.add_output("CT", val=1.25e-4, units="1/s")
    indep_var_comp.add_output("W0", val=13450.0, units="kg")
    indep_var_comp.add_output("speed_of_sound", val=309.6, units="m/s")
    indep_var_comp.add_output("load_factor", val=1.0)
    indep_var_comp.add_output("empty_cg", val=np.zeros((3)), units="m")
    indep_var_comp.add_output("WF", val=4626.0, units="kg")

    prob.model.add_subsystem("prob_vars", indep_var_comp, promotes=["*"])

    # Subsystems of geometry
    aerostruct_group = AerostructGeometry(surface=surface)
    aerostruct_group_tail = AerostructGeometry(surface=surface_tail)
    prob.model.add_subsystem(name, aerostruct_group)
    prob.model.add_subsystem(name_tail, aerostruct_group_tail)

    # Aerostruct point
    point_name = "AS_point_0"
    AS_point = AerostructPoint(surfaces=surfaces)

    prob.model.add_subsystem(
        point_name,
        AS_point,
        promotes_inputs=[
            "v", "alpha", "Mach_number", "re", "rho", "CT", "W0", "speed_of_sound", "empty_cg", "load_factor",
        ],
    )

    for surf in surfaces:
        nam = surf["name"]
        com_name = point_name + "." + nam + "_perf"

        prob.model.connect(nam + ".local_stiff_transformed", point_name + ".coupled." + nam + ".local_stiff_transformed")
        prob.model.connect(nam + ".nodes", point_name + ".coupled." + nam + ".nodes")
        prob.model.connect(nam + ".mesh", point_name + ".coupled." + nam + ".mesh")

        prob.model.connect(nam + ".radius", com_name + ".radius")
        prob.model.connect(nam + ".thickness", com_name + ".thickness")
        prob.model.connect(nam + ".nodes", com_name + ".nodes")
        prob.model.connect(nam + ".cg_location", point_name + "." + "total_perf." + nam + "_cg_location")
        prob.model.connect(nam + ".structural_mass", point_name + "." + "total_perf." + nam + "_structural_mass")
        prob.model.connect(nam + ".t_over_c", com_name + ".t_over_c")

    R_point_name = "R_point_0"
    R_point = Range(surfaces=surfaces)

    prob.model.add_subsystem(
        R_point_name,
        R_point,
        promotes_inputs=["CT", "speed_of_sound", "WF", "Mach_number", "W0"],
    )

    prob.model.connect(point_name + ".CL", R_point_name + ".CL")
    prob.model.connect(point_name + ".CD", R_point_name + ".CD")

    prob.setup(check=False)
    prob.set_solver_print(level=0)

    t0 = time.time()
    prob.run_model()
    t1 = time.time()

    # Extracts results
    def safe_get(var):
        try:
            return float(prob.get_val(var)[0])
        except Exception:
            return np.nan

    CL = safe_get(point_name + ".CL")
    CD_total = safe_get(point_name + ".CD")
    CD_wing = safe_get(point_name + ".main_wing_perf.CD")
    CD_tail = safe_get(point_name + ".tail_wing_perf.CD")
    CM_pitch = safe_get(point_name + ".CM[1]") if False else safe_get(point_name + ".CM")  # fallback
    try:
        R_km = float(prob.get_val(R_point_name + ".R", units="km")[0])
    except Exception:
        R_km = np.nan

    run_time = t1 - t0

    # cleanup to free up memory
    prob.cleanup()

    if verbose:
        print(f"run_case(nx={nx}, ny={ny}) -> CL={CL:.4f}, CD={CD_total:.5f}, CD_wing={CD_wing:.5f}, CD_tail={CD_tail:.5f}, R={R_km:.2f} km, time={run_time:.2f}s")

    return {"nx": nx, "ny": ny, "CL": CL, "CD_total": CD_total, "CD_wing": CD_wing, "CD_tail": CD_tail, "R_km": R_km, "time": run_time}

# Sweep parameters

nx_fixed = 21               
ny_list = [3, 5, 7, 9, 11, 15, 21, 31,41]   

results = []
print("\n=== CHORDWISE SWEEP (vary ny, nx_fixed = {}) ===\n".format(nx_fixed))
for ny in ny_list:
    try:
        res = run_case(nx_fixed,ny)
        results.append(res)
        print(f"ny={ny:2d}  |  CL={res['CL']:.4f}  CD={res['CD_total']:.5f}  CD_wing={res['CD_wing']:.5f}  CD_tail={res['CD_tail']:.5f}  R={res['R_km']:.2f} km  time={res['time']:.2f}s")
    except Exception as e:
        print(f"ny={ny:2d}  --> FAILED: {e}")


# Plots

ny_vals = [r["ny"] for r in results]
CD_vals = [r["CD_total"] for r in results]
time_vals = [r["time"] for r in results]
CD_wing_vals = [r["CD_wing"] for r in results]
CD_tail_vals = [r["CD_tail"] for r in results]

plt.figure(figsize=(8,4))
plt.plot(ny_vals, CD_vals, marker='o', label='CD total')
plt.xlabel("ny (spanwise panels)")
plt.ylabel("CD")
plt.title(f"CD vs ny(ny={nx_fixed})")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

plt.figure(figsize=(8,4))
plt.plot(ny_vals, time_vals, marker='o', color='red')
plt.xlabel("ny (spanwise panels)")
plt.ylabel("Run time [s]")
plt.title(f"Computational time vs ny (nx={nx_fixed})")
plt.grid(True)
plt.tight_layout()
plt.show()


# Simple convergence recommendation
def recommend_nx(results, tol_rel=0.01):
    # returns the smallest nx such that CD is within tol_rel relative to the largest nx tested
    if not results:
        return None
    max_CD = results[-1]["CD_total"]
    for r in results:
        if np.isnan(r["CD_total"]):
            continue
        if abs(r["CD_total"] - max_CD)/max_CD < tol_rel:
            return r["nx"]
    return results[-1]["nx"]

rec_nx = recommend_nx(results, tol_rel=0.01)
print("\n=== RECOMENDAÇÃO ===")
print(f"ny recomendado (CD dentro de 1% do caso mais fino): {rec_nx}")
