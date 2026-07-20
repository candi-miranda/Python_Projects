import time
import numpy as np
import matplotlib.pyplot as plt
import openmdao.api as om

from openaerostruct.geometry.utils import generate_mesh
from openaerostruct.geometry.geometry_group import Geometry
from openaerostruct.aerodynamics.aero_groups import AeroPoint

# Lista de resoluções spanwise
num_x_list = [5, 7, 9, 11, 13, 15, 17, 21]



CD_list = []
time_list = []

for nx in num_x_list:
    print(f"Running mesh with num_x = {nx}")

    # Mesh dictionary
    mesh_dict = {
    "num_y": 13,
    "num_x": nx,
    "span": 11.0,
    "wing_type": "rect",
    "symmetry": True,
}
    mesh = generate_mesh(mesh_dict)


    # Surface dictionary
    surface = {
        "name": "wing",
        "symmetry": True,
        "S_ref_type": "projected",
        "fem_model_type": "tube",
        "mesh": mesh,
        "CL0": 0.2,
        "CD0": 0.0085,
        "k_lam": 0.05,
        "t_over_c_cp": np.array([0.12]),
        "c_max_t": 0.30,
        "chord_cp": np.ones(nx) * (16.2/11.0),
        "with_viscous": True,
        "with_wave": False,
    }

    # Problem
    prob = om.Problem()

    # Flight conditions
    indep = om.IndepVarComp()
    indep.add_output("v", val=63.0, units="m/s")
    indep.add_output("alpha", val=5.0, units="deg")
    indep.add_output("Mach_number", val=0.189474)
    indep.add_output("re", val=5.41e6, units="1/m")
    indep.add_output("rho", val=1.0066, units="kg/m**3")
    indep.add_output("cg", val=np.zeros(3), units="m")
    prob.model.add_subsystem("prob_vars", indep, promotes=["*"])

    # Geometry
    geom = Geometry(surface=surface)
    prob.model.add_subsystem("wing", geom)

    # Aero analysis
    aero = AeroPoint(surfaces=[surface])
    prob.model.add_subsystem("aero_point", aero,
                             promotes_inputs=["v", "alpha", "Mach_number", "re", "rho", "cg"])

    prob.model.connect("wing.mesh", "aero_point.wing.def_mesh")
    prob.model.connect("wing.mesh", "aero_point.aero_states.wing_def_mesh")
    prob.model.connect("wing.t_over_c", "aero_point.wing_perf.t_over_c")

    prob.setup()

    # Run and time
    t0 = time.time()
    prob.run_model()
    t1 = time.time()

    CD = prob.get_val("aero_point.wing_perf.CD")[0]

    CD_list.append(CD)
    time_list.append(t1 - t0)

# Plot CD vs num_x
plt.figure(figsize=(7,4))
plt.plot(num_x_list, CD_list, marker='o')
plt.xlabel("num_x (chordwise points)")
plt.ylabel("CD")
plt.title("CD vs Mesh Resolution (x-direction)")
plt.grid(True)
plt.tight_layout()
plt.show()

# Plot computational time vs num_x
plt.figure(figsize=(7,4))
plt.plot(num_x_list, time_list, marker='o', color='red')
plt.xlabel("num_x (chordwise points)")
plt.ylabel("Computational time [s]")
plt.title("Computational Time vs Mesh Resolution (x-direction)")
plt.grid(True)
plt.tight_layout()
plt.show()
