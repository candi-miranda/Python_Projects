
"""Formulação: Otimização Aerestrutural Completa (ATR 72-600)
Estratégia: Malha leve (5x11), Scalers equilibrados, Tolerâncias relaxadas para convergência.
"""

import numpy as np
import openmdao.api as om
from openaerostruct.geometry.utils import generate_mesh
from openaerostruct.integration.aerostruct_groups import AerostructGeometry, AerostructPoint


# 1. COMPONENTE DE ALCANCE (BREGUET)

class BreguetRange(om.ExplicitComponent):
    def initialize(self):
        self.options.declare("surfaces", types=list)

    def setup(self):
        for surface in self.options["surfaces"]:
            self.add_input(surface["name"] + "_structural_mass", val=1.0, units="kg")
        self.add_input("CT", val=1.25e-4, units="1/s")
        self.add_input("CL", val=0.5)
        self.add_input("CD", val=0.02)
        self.add_input("speed_of_sound", val=309.6, units="m/s")
        self.add_input("WF", val=4626.0, units="kg")
        self.add_input("Mach_number", val=0.443)
        self.add_input("W0", val=13450.0, units="kg")
        self.add_output("Range", val=1e3, units="m")
        self.declare_partials("*", "*", method="cs")

    def compute(self, inputs, outputs):
        CT, a, WF, M, W0 = inputs["CT"], inputs["speed_of_sound"], inputs["WF"], inputs["Mach_number"], inputs["W0"]
        Ws = sum([inputs[s["name"] + "_structural_mass"] for s in self.options["surfaces"]])
        outputs["Range"] = M * a * inputs["CL"] / inputs["CD"] / CT * np.log(1 + WF / (W0 + Ws))


# 2. PERFIL NACA E MALHAS (NATIVO E OTIMIZADO)

def naca4_wingbox(m, p, t, num=20):
    x = np.linspace(0.15, 0.60, num)
    yt = 5.0 * t * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * (x**2) + 0.2843 * (x**3) - 0.1015 * (x**4))
    yc = np.where(x <= p, (m / p**2) * (2*p*x - x**2), (m / (1-p)**2) * ((1-2*p) + 2*p*x - x**2)) if p > 0 else np.zeros_like(x)
    dyc_dx = np.where(x <= p, (2*m / p**2) * (p - x), (2*m / (1-p)**2) * (p - x)) if p > 0 else np.zeros_like(x)
    theta = np.arctan(dyc_dx)
    return (x - yt*np.sin(theta)).astype("complex128"), (x + yt*np.sin(theta)).astype("complex128"), (yc + yt*np.cos(theta)).astype("complex128"), (yc - yt*np.cos(theta)).astype("complex128")

w_xu, w_xl, w_yu, w_yl = naca4_wingbox(0.04, 0.3, 0.18)
t_xu, t_xl, t_yu, t_yl = naca4_wingbox(0.00, 0.0, 0.09)

# Malha rápida para permitir procura intensiva do otimizador (5 na corda, 11 na envergadura)
mesh_wing = generate_mesh({"num_y": 11, "num_x": 5, "wing_type": "rect", "symmetry": True, "span": 27.05, "root_chord": 3.11})
mesh_tail = generate_mesh({"num_y": 11, "num_x": 5, "wing_type": "rect", "symmetry": True, "span": 8.49, "root_chord": 1.8845})
mesh_tail[:, :, 0] += 12.0


# 3. SUPERFÍCIES

surf_wing = {
    "name": "wing", "symmetry": True, "S_ref_type": "projected", "fem_model_type": "wingbox", "mesh": mesh_wing,
    "span": 27.05, "sweep": 3.0, "taper": 0.45,
    "data_x_upper": w_xu, "data_x_lower": w_xl, "data_y_upper": w_yu, "data_y_lower": w_yl,
    
    # Valores de arranque
    "spar_thickness_cp": np.array([0.015, 0.005]), "skin_thickness_cp": np.array([0.010, 0.004]),
    "twist_cp": np.zeros(3), 
    
    "t_over_c_cp": np.array([0.18, 0.13]), "original_wingbox_airfoil_t_over_c": 0.18,
    "CL0": 0.15, "CD0": 0.015, "with_wave": False, "with_viscous": True, "k_lam": 0.05, "c_max_t": 0.30,
    "E": 71.7e9, "G": 26.9e9, "yield": 503.0e6 / 3.36, "mrho": 2.81e3, "wing_weight_ratio": 1.5,
    "strength_factor_for_upper_skin": 1.0, "struct_weight_relief": True, "distributed_fuel_weight": True,
    "exact_failure_constraint": False, "Wf_reserve": 0.0, "fuel_density": 820.0
}

surf_tail = {
    "name": "tail", "symmetry": True, "S_ref_type": "projected", "fem_model_type": "wingbox", "mesh": mesh_tail,
    "span": 8.49, "sweep": 0.0, "taper": 1.0,
    "data_x_upper": t_xu, "data_x_lower": t_xl, "data_y_upper": t_yu, "data_y_lower": t_yl,
    
    "spar_thickness_cp": np.array([0.005, 0.002]), "skin_thickness_cp": np.array([0.004, 0.002]),
    "twist_cp": np.zeros(1), 
    
    "t_over_c_cp": np.array([0.09]), "original_wingbox_airfoil_t_over_c": 0.09,
    "CL0": 0.0, "CD0": 0.015, "with_wave": False, "with_viscous": True, "k_lam": 0.05, "c_max_t": 0.30,
    "E": 71.7e9, "G": 26.9e9, "yield": 503.0e6 / 3.36, "mrho": 2.81e3, "wing_weight_ratio": 1.25,
    "strength_factor_for_upper_skin": 1.0, "struct_weight_relief": True, "distributed_fuel_weight": False,
    "exact_failure_constraint": False, "Wf_reserve": 0.0, "fuel_density": 820.0
}
surfaces = [surf_wing, surf_tail]


# 4. PROBLEMA E CONEXÕES OPENMDAO

prob = om.Problem()
ivc = om.IndepVarComp()

ivc.add_output("v", val=np.array([137.2, 102.1]), units="m/s")
ivc.add_output("Mach_number", val=np.array([0.443, 0.30]))
ivc.add_output("re", val=np.array([4.9e6, 7.0e6]), units="1/m")
ivc.add_output("rho", val=np.array([0.549, 1.225]), units="kg/m**3")
ivc.add_output("speed_of_sound", val=np.array([309.6, 340.3]), units="m/s")
ivc.add_output("CT", val=1.25e-4, units="1/s")
ivc.add_output("W0", val=13450.0, units="kg")
ivc.add_output("WF", val=4626.0, units="kg")
ivc.add_output("load_factor", val=np.array([1.0, 2.5]))
ivc.add_output("empty_cg", val=np.array([1.2, 0.0, 0.0]), units="m") 

ivc.add_output("alpha", val=0.0, units="deg")
ivc.add_output("alpha_maneuver", val=0.0, units="deg")
ivc.add_output("wing_span", val=27.05, units="m")
ivc.add_output("tail_span", val=8.49, units="m")
ivc.add_output("wing_sweep", val=3.0, units="deg")

prob.model.add_subsystem("ivc", ivc, promotes=["*"])
for surf in surfaces: prob.model.add_subsystem(surf["name"], AerostructGeometry(surface=surf))

prob.model.connect("wing_span", "wing.geometry.span")
prob.model.connect("tail_span", "tail.geometry.span")
prob.model.connect("wing_sweep", "wing.sweep")

for i in range(2):
    pname = f"AS_point_{i}"
    prob.model.add_subsystem(pname, AerostructPoint(surfaces=surfaces, internally_connect_fuelburn=False))
    
    for var in ["v", "Mach_number", "re", "rho", "speed_of_sound", "load_factor"]:
        prob.model.connect(var, f"{pname}.{var}", src_indices=[i])
    prob.model.connect("load_factor", f"{pname}.coupled.load_factor", src_indices=[i])
    for var in ["CT", "W0", "empty_cg"]: prob.model.connect(var, f"{pname}.{var}")
    
    prob.model.connect("alpha" if i==0 else "alpha_maneuver", f"{pname}.alpha")

    for surf in surfaces:
        name = surf["name"]
        cname = f"{pname}.{name}_perf."
        prob.model.connect(f"{name}.local_stiff_transformed", f"{pname}.coupled.{name}.local_stiff_transformed")
        prob.model.connect(f"{name}.nodes", f"{pname}.coupled.{name}.nodes")
        prob.model.connect(f"{name}.mesh", f"{pname}.coupled.{name}.mesh")
        prob.model.connect(f"{name}.nodes", cname + "nodes")
        prob.model.connect(f"{name}.cg_location", f"{pname}.total_perf.{name}_cg_location")
        prob.model.connect(f"{name}.structural_mass", f"{pname}.total_perf.{name}_structural_mass")
        for prop in ["Qz", "J", "A_enc", "htop", "hbottom", "hfront", "hrear", "spar_thickness", "t_over_c"]:
            prob.model.connect(f"{name}.{prop}", cname + prop)

prob.model.add_subsystem("RangeCalc", BreguetRange(surfaces=surfaces), promotes_inputs=["CT", "WF", "W0"])

# Ligar aos valores de performance global
prob.model.connect("AS_point_0.total_perf.CL", "RangeCalc.CL")
prob.model.connect("AS_point_0.total_perf.CD", "RangeCalc.CD")

prob.model.connect("Mach_number", "RangeCalc.Mach_number", src_indices=[0])
prob.model.connect("speed_of_sound", "RangeCalc.speed_of_sound", src_indices=[0])
prob.model.connect("wing.structural_mass", "RangeCalc.wing_structural_mass")
prob.model.connect("tail.structural_mass", "RangeCalc.tail_structural_mass")


# 5. OTIMIZADOR (AERESTRUTURAL TOTAL)

prob.driver = om.ScipyOptimizeDriver(optimizer="SLSQP", tol=1e-3, maxiter=150)

# Gravador ajustado exatamente para o nome que o plot_aerostruct.py procura
recorder = om.SqliteRecorder("aerostruct.db")
prob.driver.add_recorder(recorder)
prob.model.recording_options["record_outputs"] = True
prob.model.recording_options["record_inputs"] = True
prob.model.recording_options["record_residuals"] = True

prob.model.add_recorder(recorder)
prob.driver.recording_options["includes"] = ['*']

# Variáveis Aerodinâmicas
prob.model.add_design_var("alpha", lower=-5.0, upper=15.0, units="deg", scaler=0.1)
prob.model.add_design_var("alpha_maneuver", lower=-5.0, upper=15.0, units="deg", scaler=0.1)
prob.model.add_design_var("wing.twist_cp", lower=-10.0, upper=10.0, units="deg", scaler=0.1)
prob.model.add_design_var("tail.twist_cp", lower=-15.0, upper=15.0, units="deg", scaler=0.1)
prob.model.add_design_var("wing_span", lower=20.0, upper=35.0, units="m", scaler=0.01)
prob.model.add_design_var("tail_span", lower=7.0, upper=12.0, units="m", scaler=0.1) 
prob.model.add_design_var("wing_sweep", lower=0.0, upper=15.0, units="deg", scaler=0.1)

# Variáveis Estruturais
prob.model.add_design_var("wing.spar_thickness_cp", lower=0.005, upper=0.1, scaler=1e2)
prob.model.add_design_var("wing.skin_thickness_cp", lower=0.005, upper=0.1, scaler=1e2)
prob.model.add_design_var("tail.spar_thickness_cp", lower=0.002, upper=0.1, scaler=1e2)
prob.model.add_design_var("tail.skin_thickness_cp", lower=0.002, upper=0.1, scaler=1e2)

# Restrições de Voo e Integridade
prob.model.add_constraint("AS_point_0.L_equals_W", equals=0.0, scaler=1.0)
prob.model.add_constraint("AS_point_1.L_equals_W", equals=0.0, scaler=1.0)
prob.model.add_constraint("AS_point_0.CM", indices=[1], lower=-1e-3, upper=1e-3, scaler=1e1) 
prob.model.add_constraint("AS_point_1.wing_perf.failure", upper=0.0)
prob.model.add_constraint("AS_point_1.tail_perf.failure", upper=0.0)

# Objetivo: Maximizar Alcance
prob.model.add_objective("RangeCalc.Range", scaler=-1e-4)


# 6. SETUP E SOLUÇÃO

prob.setup()

# Geração do N2 Diagram 
om.n2(prob, outfile='n2_aerostrutural.html', show_browser=False)

prob.model.AS_point_0.coupled.linear_solver = om.LinearBlockGS(iprint=0, maxiter=30, use_aitken=True)
prob.model.AS_point_1.coupled.linear_solver = om.LinearBlockGS(iprint=0, maxiter=30, use_aitken=True)

prob.model.AS_point_0.coupled.nonlinear_solver.options['atol'] = 1e-4
prob.model.AS_point_0.coupled.nonlinear_solver.options['rtol'] = 1e-4
prob.model.AS_point_1.coupled.nonlinear_solver.options['atol'] = 1e-4
prob.model.AS_point_1.coupled.nonlinear_solver.options['rtol'] = 1e-4

print("\nIniciando Otimização Aerestrutural. Processo ajustado e focado...")
prob.run_driver()


# Output dos resultados

print("\n" + "="*70)
print("RESULTADOS DA OTIMIZAÇÃO AERESTRUTURAL FINAL (ATR 72-600)")
print("="*70)

print("The Range value is", prob.get_val("RangeCalc.Range", units="km")[0], "[km]")
print("The wingbox mass is", prob.get_val("wing.structural_mass")[0] / surf_wing["wing_weight_ratio"], "[kg]")

print("\n--- Variáveis de Voo e Forma Otimizadas ---")
print("alpha =", prob.get_val("alpha")[0], "deg")
print("alpha 2.5g =", prob.get_val("alpha_maneuver")[0], "deg")
print("sweep =", prob.get_val("wing_sweep")[0], "deg")
print("span =", prob.get_val("wing_span")[0], "m")
print("tail span =", prob.get_val("tail_span")[0], "m")
print("wing twist_cp =", prob.get_val("wing.twist_cp"))
print("tail twist_cp =", prob.get_val("tail.twist_cp"))

print("\n--- Espessuras Estruturais Otimizadas ---")
print("wing spar thickness =", prob.get_val("wing.spar_thickness_cp"))
print("wing skin thickness =", prob.get_val("wing.skin_thickness_cp"))
print("tail spar thickness =", prob.get_val("tail.spar_thickness_cp"))
print("tail skin thickness =", prob.get_val("tail.skin_thickness_cp"))

print("\n--- Performance e Restrições ---")
print("C_D =", prob.get_val("AS_point_0.total_perf.CD")[0])
print("C_L =", prob.get_val("AS_point_0.total_perf.CL")[0])
print("CM vector =", prob.get_val("AS_point_0.CM"))
try:
    print("CG vector =", prob.get_val("AS_point_0.cg"))
except KeyError:
    print("CG vector =", prob.get_val("AS_point_0.total_perf.cg"))
print("AS_point_0.L_equals_W =", prob.get_val("AS_point_0.L_equals_W")[0])
print("AS_point_1.L_equals_W =", prob.get_val("AS_point_1.L_equals_W")[0])
print("Wing Failure (2.5g) =", prob.get_val("AS_point_1.wing_perf.failure").max())
print("Tail Failure (2.5g) =", prob.get_val("AS_point_1.tail_perf.failure").max())

print("="*70)
prob.cleanup()