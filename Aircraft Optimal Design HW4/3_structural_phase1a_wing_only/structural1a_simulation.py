"""
Projeto: Otimização Estrutural ATR 72-600 
Objetivo: Redução de peso estrutural mantendo a geometria fixa.
Maximização de Alcance (Breguet) via redução de peso morto.
"""

import numpy as np
import openmdao.api as om
from openaerostruct.geometry.utils import generate_mesh
from openaerostruct.integration.aerostruct_groups import AerostructGeometry, AerostructPoint
from math import sqrt


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


# 2. GERADOR NACA E MALHAS

def naca4_wingbox(m, p, t, num=20):
    x = np.linspace(0.15, 0.60, num)
    yt = 5.0 * t * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * (x**2) + 0.2843 * (x**3) - 0.1015 * (x**4))
    yc = np.where(x <= p, (m / p**2) * (2*p*x - x**2), (m / (1-p)**2) * ((1-2*p) + 2*p*x - x**2)) if p > 0 else np.zeros_like(x)
    dyc_dx = np.where(x <= p, (2*m / p**2) * (p - x), (2*m / (1-p)**2) * (p - x)) if p > 0 else np.zeros_like(x)
    theta = np.arctan(dyc_dx)
    return (x - yt*np.sin(theta)).astype("complex128"), (x + yt*np.sin(theta)).astype("complex128"), (yc + yt*np.cos(theta)).astype("complex128"), (yc - yt*np.cos(theta)).astype("complex128")

w_xu, w_xl, w_yu, w_yl = naca4_wingbox(0.04, 0.3, 0.18)
t_xu, t_xl, t_yu, t_yl = naca4_wingbox(0.00, 0.0, 0.09)

mesh_wing = generate_mesh({"num_y": 15, "num_x": 15, "wing_type": "rect", "symmetry": True, "span": 27.05, "root_chord": 3.11})
mesh_tail = generate_mesh({"num_y": 15, "num_x": 15, "wing_type": "rect", "symmetry": True, "span": 8.49, "root_chord": 1.8845})
mesh_tail[:, :, 0] += 12.0

# 3. DICIONÁRIOS DAS SUPERFÍCIES

surf_wing = {
    "name": "wing", "symmetry": True, "S_ref_type": "projected", "fem_model_type": "wingbox", "mesh": mesh_wing,
    "data_x_upper": w_xu, "data_x_lower": w_xl, "data_y_upper": w_yu, "data_y_lower": w_yl,
    
    # Geometria estática de fábrica (Não será otimizada nesta fase)
    "span": 27.05, "sweep": 3.0, "taper": 0.45,
    
    "spar_thickness_cp": np.array([0.015, 0.005]), "skin_thickness_cp": np.array([0.010, 0.004]),
    "twist_cp": np.zeros(3), "t_over_c_cp": np.array([0.18, 0.13]), "original_wingbox_airfoil_t_over_c": 0.18,
    "CL0": 0.15, "CD0": 0.015, "with_wave": False, "with_viscous": True, "k_lam": 0.05, "c_max_t": 0.30,
    "E": 71.7e9, "G": 26.9e9, "yield": 503.0e6 / 3.36, "mrho": 2.81e3, "wing_weight_ratio": 1.5,
    "strength_factor_for_upper_skin": 1.0, "struct_weight_relief": True, "distributed_fuel_weight": True,
    "exact_failure_constraint": False, "Wf_reserve": 0.0, "fuel_density": 820.0
}

surf_tail = {
    "name": "tail", "symmetry": True, "S_ref_type": "projected", "fem_model_type": "wingbox", "mesh": mesh_tail,
    "data_x_upper": t_xu, "data_x_lower": t_xl, "data_y_upper": t_yu, "data_y_lower": t_yl,
    "span": 8.49, "sweep": 0.0, "taper": 1.0,
    "spar_thickness_cp": np.array([0.005, 0.002]), "skin_thickness_cp": np.array([0.004, 0.002]),
    "twist_cp": np.zeros(1), "t_over_c_cp": np.array([0.09]), "original_wingbox_airfoil_t_over_c": 0.09,
    "CL0": 0.0, "CD0": 0.015, "with_wave": False, "with_viscous": True, "k_lam": 0.05, "c_max_t": 0.30,
    "E": 71.7e9, "G": 26.9e9, "yield": 503.0e6 / 3.36, "mrho": 2.81e3, "wing_weight_ratio": 1.25,
    "strength_factor_for_upper_skin": 1.0, "struct_weight_relief": True, "distributed_fuel_weight": False,
    "exact_failure_constraint": False, "Wf_reserve": 0.0, "fuel_density": 820.0
}
surfaces = [surf_wing, surf_tail]

# 4. SETUP DO PROBLEMA E FÍSICA

prob = om.Problem()

# Atmosfera
altitude = np.array([25000 * 0.3048, 0])  # Cruzeiro e Manobra
temperature = 288.15 - 0.0065 * altitude
density = np.array([1.225 * (1 - (0.0065 * altitude[0]) / 288.15) ** 4.2558, 
                    1.225 * (1 - (0.0065 * altitude[1]) / 288.15) ** 4.2558])
R_gas = 287.052874
gamma = 1.403
mach = np.array([0.443, 0.30])
c = np.array([sqrt(gamma * R_gas * temperature[0]), sqrt(gamma * R_gas * temperature[1])])
velocity = mach * c
Re = density * velocity / (1.4 * 1e-5)

ivc = om.IndepVarComp()
ivc.add_output("Mach_number", val=mach)
ivc.add_output("v", val=velocity, units="m/s")
ivc.add_output("re", val=Re, units="1/m")
ivc.add_output("rho", val=density, units="kg/m**3")
ivc.add_output("speed_of_sound", val=c, units="m/s")

ivc.add_output("CT", val=1.25e-4, units="1/s")
ivc.add_output("W0", val=13450.0, units="kg")
ivc.add_output("WF", val=4626.0, units="kg")
ivc.add_output("load_factor", val=np.array([1.0, 2.5]))
ivc.add_output("empty_cg", val=np.array([1.2, 0.0, 0.0]), units="m")

# Variáveis do trim 
ivc.add_output("alpha", val=0.0, units="deg")
ivc.add_output("alpha_maneuver", val=0.0, units="deg")

# Constantes Geométricas
ivc.add_output("wing_span", val=27.05, units="m")
ivc.add_output("wing_sweep", val=3.0, units="deg")
ivc.add_output("tail_span", val=7.43, units="m")

prob.model.add_subsystem("ivc", ivc, promotes=["*"])
for surf in surfaces: prob.model.add_subsystem(surf["name"], AerostructGeometry(surface=surf))

prob.model.connect("wing_span", "wing.geometry.span")
prob.model.connect("wing_sweep", "wing.sweep") 
prob.model.connect("tail_span", "tail.geometry.span")

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
prob.model.connect("AS_point_0.CL", "RangeCalc.CL")
prob.model.connect("AS_point_0.CD", "RangeCalc.CD")
prob.model.connect("Mach_number", "RangeCalc.Mach_number", src_indices=[0])
prob.model.connect("speed_of_sound", "RangeCalc.speed_of_sound", src_indices=[0])
prob.model.connect("wing.structural_mass", "RangeCalc.wing_structural_mass")
prob.model.connect("tail.structural_mass", "RangeCalc.tail_structural_mass")

# 5. OTIMIZADOR 

prob.driver = om.ScipyOptimizeDriver(optimizer="SLSQP", tol=1e-3, maxiter=40)

# Gravador SQLite para análise posterior
recorder = om.SqliteRecorder("ATR72_opti_estrutural.db")
prob.driver.add_recorder(recorder)
prob.driver.recording_options["includes"] = ['*']

# Variáveis de design
# 1. Variáveis de Trimagem (Obrigatórias para voar)
prob.model.add_design_var("alpha", lower=-5.0, upper=15.0, units="deg")
prob.model.add_design_var("alpha_maneuver", lower=-5.0, upper=15.0, units="deg")
prob.model.add_design_var("tail.twist_cp", lower=-15.0, upper=15.0, units="deg")

# 2. Variáveis Estruturais (Os alvos de otimização)
prob.model.add_design_var("wing.spar_thickness_cp", lower=0.002, upper=0.05, scaler=1e3)
prob.model.add_design_var("wing.skin_thickness_cp", lower=0.002, upper=0.05, scaler=1e3)
#prob.model.add_design_var("tail.spar_thickness_cp", lower=0.001, upper=0.05, scaler=1e3)
#prob.model.add_design_var("tail.skin_thickness_cp", lower=0.001, upper=0.05, scaler=1e3)


# Restrições
prob.model.add_constraint("AS_point_0.L_equals_W", equals=0.0, scaler=1e-5)
prob.model.add_constraint("AS_point_1.L_equals_W", equals=0.0, scaler=1e-5)
prob.model.add_constraint("AS_point_0.CM", indices=[1], lower=-1e-4, upper=1e-4, scaler=1e3) 
prob.model.add_constraint("AS_point_1.wing_perf.failure", upper=0.0)
prob.model.add_constraint("AS_point_1.tail_perf.failure", upper=0.0)

# Objetivo
prob.model.add_objective("RangeCalc.Range", scaler=-1e-4)

# 6. SETUP E RESOLUÇÃO

prob.setup()

# Gestão de Memória
prob.model.AS_point_0.coupled.linear_solver = om.LinearBlockGS(iprint=0, maxiter=30, use_aitken=True)
prob.model.AS_point_1.coupled.linear_solver = om.LinearBlockGS(iprint=0, maxiter=30, use_aitken=True)

# Relaxamento das tolerâncias não lineares
prob.model.AS_point_0.coupled.nonlinear_solver.options['atol'] = 1e-4
prob.model.AS_point_0.coupled.nonlinear_solver.options['rtol'] = 1e-4
prob.model.AS_point_1.coupled.nonlinear_solver.options['atol'] = 1e-4
prob.model.AS_point_1.coupled.nonlinear_solver.options['rtol'] = 1e-4

print("\n" + "="*70)
print("INICIANDO OTIMIZAÇÃO ESTRUTURAL (ATR 72-600)")
print("="*70)

prob.run_driver()


# 7. TELEMETRIA FASE 1

print("\n" + "="*70)
print("RESULTADOS DA OTIMIZAÇÃO ESTRUTURAL")
print("="*70)

print("Range Máximo Otimizado =", prob.get_val("RangeCalc.Range", units="km")[0], "[km]")
print("Massa da Asa (Wingbox) =", prob.get_val("wing.structural_mass")[0] / surf_wing["wing_weight_ratio"], "[kg]")

print("\n--- Trim Variables ---")
print("alpha =", prob.get_val("alpha", units="deg"))
print("alpha_maneuver =", prob.get_val("alpha_maneuver", units="deg"))
print("tail_twist_cp =", prob.get_val("tail.twist_cp", units="deg"))

print("\n--- Espessuras Finais Otimizadas (Copiar para a Fase Seguinte) ---")
print("wing_spar_thickness =", prob.get_val("wing.spar_thickness_cp"))
print("wing_skin_thickness =", prob.get_val("wing.skin_thickness_cp"))

print("\n--- Restrições de Segurança (Devem estar próximas de 0.0) ---")
print("Wing Failure (max a 2.5g) =", prob.get_val("AS_point_1.wing_perf.failure").max())
print("Tail Failure (max a 2.5g) =", prob.get_val("AS_point_1.tail_perf.failure").max())
print("CM vector =", prob.get_val("AS_point_0.CM"))

print("="*70)
prob.cleanup()