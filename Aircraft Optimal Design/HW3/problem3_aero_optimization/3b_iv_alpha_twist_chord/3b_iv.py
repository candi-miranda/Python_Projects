# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import openmdao.api as om

os.environ['OPENMDAO_REPORTS'] = '0'

from openaerostruct.geometry.utils import generate_mesh
from openaerostruct.geometry.geometry_group import Geometry
from openaerostruct.aerodynamics.aero_groups import AeroPoint

Area = 16.2
Span = 11.0
Chord_baseline = Area / Span

mesh_dict = {
    "num_y" : 13,
    "num_x" : 11,
    "wing_type" : "rect",
    "symmetry" : True,
    "span": Span,
    "chord": Chord_baseline,
}

mesh = generate_mesh(mesh_dict)

# CORDA LINEAR REAL (2 Pontos) + TORÇÃO (4 Pontos)
points_chord = 2
chord_cp = np.array([Chord_baseline, 0.5]) 

points_twist = 4
twist = np.zeros(points_twist)

surface = {
    "name" : "wing",         
    "symmetry" : True,       
    "S_ref_type": "projected",  
    "fem_model_type" : "tube",
    "mesh" : mesh,
    "chord_cp": chord_cp,
    "twist_cp": twist,
    "CL0" : 0.22,    
    "CD0" : 0.008,  
    "k_lam" : 0.05,  
    "t_over_c_cp" : np.array([0.12]),  
    "c_max_t" : 0.30,  
    "with_viscous" : True,  # Mantemos True para o teu estudo viscoso real
    "with_wave" : False,    
}

prob = om.Problem()

indep_var_comp = om.IndepVarComp()
indep_var_comp.add_output("v", val=63, units="m/s")
indep_var_comp.add_output("alpha", val=5.0, units="deg")
indep_var_comp.add_output("Mach_number", val=0.189474) 
indep_var_comp.add_output("re", val=5.41e6, units="1/m") 
indep_var_comp.add_output("rho", val=1.0066, units="kg/m**3") 
indep_var_comp.add_output("cg", val=np.zeros((3)), units="m")

prob.model.add_subsystem("prob_vars", indep_var_comp, promotes=["*"])

geom_group = Geometry(surface=surface)
prob.model.add_subsystem(surface["name"], geom_group)

aero_point_group = AeroPoint(surfaces=[surface])
point_name = "aero_point_0"
prob.model.add_subsystem(point_name, aero_point_group,
                         promotes_inputs=["v", "alpha", "Mach_number", "re", "rho", "cg"]
)

name = surface["name"]
prob.model.connect(name + ".mesh", point_name + "." + name + ".def_mesh")
prob.model.connect(name + ".mesh", point_name + ".aero_states." + name + "_def_mesh")
prob.model.connect(name + ".t_over_c", point_name + ".wing_perf.t_over_c")

prob.driver = om.ScipyOptimizeDriver()
prob.driver.options["tol"] = 1e-9

recorder = om.SqliteRecorder("aero_linear_total.db")
prob.driver.add_recorder(recorder)
prob.driver.recording_options['includes'] = ['*']

# VARIÁVEIS DE DESIGN SINTONIZADAS
prob.model.add_design_var("alpha", lower=-5.0, upper=15.0) 
prob.model.add_design_var("wing.chord_cp", lower=[0.5] * points_chord, upper=[3.0] * points_chord)
prob.model.add_design_var("wing.twist_cp", lower=-10.0, upper=15.0, indices=np.arange(1, points_twist), units="deg")

prob.model.add_constraint(point_name + ".wing_perf.CL", equals=0.357)
prob.model.add_constraint(point_name + ".wing_perf.S_ref", equals=Area)
prob.model.add_constraint(point_name + ".wing_perf.Cl", upper=1.5)

prob.model.add_objective(point_name + ".wing_perf.CD", scaler=1e4)

prob.setup()
prob.run_driver()

print("=== OTIMIZAÇÃO TOTAL CONVERGIDA ===")
print("CD Total =", prob['aero_point_0.wing_perf.CD'][0])
print("CL Total =", prob['aero_point_0.wing_perf.CL'][0])
print("S_ref    =", prob['aero_point_0.wing_perf.S_ref'][0])
print("Alpha    =", prob['alpha'][0])
print("Twist_cp =", prob['wing.twist_cp'])
print("Chord_cp =", prob['wing.chord_cp'])

prob.cleanup()