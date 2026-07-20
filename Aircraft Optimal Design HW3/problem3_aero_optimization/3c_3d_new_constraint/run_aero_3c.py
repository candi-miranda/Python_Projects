# -*- coding: utf-8 -*-
import os
os.environ['OPENMDAO_REPORTS'] = '0'
import numpy as np
import openmdao.api as om

from openaerostruct.meshing.mesh_generator import generate_mesh
from openaerostruct.geometry.geometry_group import Geometry
from openaerostruct.aerodynamics.aero_groups import AeroPoint

from efficiency_comp import AeroEfficiency

mesh_dict = {"num_y": 13, "num_x": 11, "span": 11, "wing_type": "rect", "symmetry": True}
mesh = generate_mesh(mesh_dict)

Area = 16.2
Span = 11
Chord = Area / Span

points_twist = 4
twist = np.zeros(points_twist)

points_chord = 2
chord_cp = np.array([Chord, 0.5]) 

surface = {
    "name": "wing",
    "symmetry": True,
    "S_ref_type": "projected",
    "fem_model_type": "tube",
    "mesh": mesh,
    "CL0": 0.22,   
    "CD0": 0.008,  
    "k_lam": 0.05, 
    "t_over_c_cp": np.array([0.12]),  
    "c_max_t": 0.30,  
    "chord_cp": chord_cp,
    "twist_cp": twist,
    "with_viscous": True,  
    "with_wave": False,
}


prob = om.Problem()


indep_var_comp = om.IndepVarComp()
indep_var_comp.add_output("v", val=63, units="m/s")
indep_var_comp.add_output("alpha", val=5.0, units="deg")
indep_var_comp.add_output("Mach_number", val=0.189526)
indep_var_comp.add_output("re", val=5.457e6, units="1/m") 
indep_var_comp.add_output("rho", val=1.006967, units="kg/m**3") 
indep_var_comp.add_output("cg", val=np.zeros((3)), units="m")

prob.model.add_subsystem("prob_vars", indep_var_comp, promotes=["*"])


geom_group = Geometry(surface=surface)
prob.model.add_subsystem(surface["name"], geom_group)

aero_group = AeroPoint(surfaces=[surface])
point_name = "aero_point_0"
prob.model.add_subsystem(point_name, aero_group, promotes_inputs=["v", "alpha", "Mach_number", "re", "rho", "cg"])


prob.model.connect("wing.mesh", point_name + ".wing.def_mesh")
prob.model.connect("wing.mesh", point_name + ".aero_states.wing_def_mesh")
prob.model.connect("wing.t_over_c", point_name + ".wing_perf.t_over_c")

prob.model.add_subsystem('efficiency_analysis', AeroEfficiency())


prob.model.connect(point_name + ".wing_perf.CL", 'efficiency_analysis.CL')
prob.model.connect(point_name + ".wing_perf.CD", 'efficiency_analysis.CD')


prob.driver = om.ScipyOptimizeDriver()
prob.driver.options["tol"] = 1e-9  


recorder = om.SqliteRecorder("aero_optimization.db")
prob.driver.add_recorder(recorder)
prob.driver.recording_options["record_derivatives"] = True
prob.driver.recording_options["includes"] = ["*"]


prob.model.add_design_var("alpha", lower=-5.0, upper=15.0, units="deg")
prob.model.add_design_var("wing.chord_cp", lower=[0.5]*points_chord, upper=[3.0]*points_chord)
prob.model.add_design_var("wing.twist_cp", lower=-10.0, upper=15.0, indices=np.arange(1, points_twist), units="deg")


prob.model.add_constraint(point_name + ".wing_perf.CL", equals=0.357)
prob.model.add_constraint(point_name + ".wing_perf.S_ref", equals=Area)
prob.model.add_constraint(point_name + ".wing_perf.Cl", upper=1.5)


prob.model.add_constraint('efficiency_analysis.eff', lower=24.0)


prob.model.add_objective(point_name + ".wing_perf.CD", scaler=1e4)


prob.setup()
prob.driver.add_recorder(recorder)
prob.run_driver()



print(f"Ângulo de Ataque (Alpha) ótimo: {prob.get_val('alpha')[0]:.4f}º")
print(f"CL alcançado: {prob.get_val(point_name + '.wing_perf.CL')[0]:.4f}")
print(f"CD Total alcançado: {prob.get_val(point_name + '.wing_perf.CD')[0]:.5f}")
print(f"FINEZA AERODINÂMICA (C_L/C_D): {prob.get_val('efficiency_analysis.eff')[0]:.2f}")
print(f"Distribuição de Cordas Ótima: {prob.get_val('wing.chord_cp')}")
print(f"Distribuição de Torções Ótima: {prob.get_val('wing.twist_cp')}")
