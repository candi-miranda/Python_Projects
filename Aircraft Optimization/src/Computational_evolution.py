import matplotlib.pyplot as plt
import openmdao.api as om
import numpy as np

# 1. Ler o histórico da otimização
cr = om.CaseReader("aerostruct.db")
driver_cases = cr.get_cases('driver', recurse=False)

# 2. Listas para guardar histórico
range_values = []

alpha_values = []
alpha_maneuver_values = []

wing_twist_values = []
tail_twist_values = []

wing_span_values = []
tail_span_values = []
wing_sweep_values = []

wing_spar_values = []
wing_skin_values = []

AS_point0_LequalsW_values = []
AS_point1_LequalsW_values = []
AS_point0_CM_values = []
AS_point1_wing_fail_values = []
AS_point1_tail_fail_values = []

# 3. Extrair valores de cada iteração 
for case in driver_cases:
    # Objetivo
    range_values.append(case['RangeCalc.Range']/1000)

    # Trim
    alpha_values.append(case['alpha'])
    alpha_maneuver_values.append(case['alpha_maneuver'])

    # Twist
    wing_twist_values.append(case['wing.twist_cp'])
    tail_twist_values.append(case['tail.twist_cp'])

    # Geometria
    wing_span_values.append(case['wing.geometry.span'])
    tail_span_values.append(case['tail.geometry.span'])
    wing_sweep_values.append(case['wing.sweep'])

    # Estrutura
    wing_spar_values.append(case['wing.spar_thickness_cp'])
    wing_skin_values.append(case['wing.skin_thickness_cp'])

    # Constraints
    AS_point0_LequalsW_values.append(case['AS_point_0.L_equals_W'])
    AS_point1_LequalsW_values.append(case['AS_point_1.L_equals_W'])
    AS_point0_CM_values.append(case['AS_point_0.CM'])
    AS_point1_wing_fail_values.append(case['AS_point_1.wing_perf.failure'])
    AS_point1_tail_fail_values.append(case['AS_point_1.tail_perf.failure'])

iters = np.arange(len(driver_cases))

# Range 
plt.figure(figsize=(8,5))
plt.plot(iters, range_values)
plt.title("Range ao longo das iterações")
plt.xlabel("Iteração")
plt.ylabel("Range [km]")
plt.grid()
plt.tight_layout()
plt.show()

# Trim 
plt.figure(figsize=(8,5))
plt.plot(iters, alpha_values)
plt.plot(iters, alpha_maneuver_values)
plt.title("Evolução dos ângulos de ataque")
plt.xlabel("Iteração")
plt.ylabel("Ângulos [deg]")
plt.legend(["alpha", "alpha_maneuver"])
plt.grid()
plt.tight_layout()
plt.show()

# Twist
plt.figure(figsize=(8,5))
plt.plot(iters, np.array(wing_twist_values)[:,0])
plt.plot(iters, np.array(wing_twist_values)[:,1])
plt.plot(iters, np.array(wing_twist_values)[:,2])
plt.plot(iters, np.array(tail_twist_values))
plt.title("Twist da asa e cauda")
plt.xlabel("Iteração")
plt.ylabel("Twist [deg]")
plt.legend(["Wing tip", "Wing mid", "Wing root", "Tail"])
plt.grid()
plt.tight_layout()
plt.show()

# Wing thickness
plt.figure(figsize=(8,5))
plt.plot(iters, np.array(wing_spar_values)[:,0])
plt.plot(iters, np.array(wing_spar_values)[:,1])
plt.plot(iters, np.array(wing_skin_values)[:,0])
plt.plot(iters, np.array(wing_skin_values)[:,1])
plt.title("Espessuras estruturais da asa")
plt.xlabel("Iteração")
plt.ylabel("Espessura [m]")
plt.legend(["spar root", "spar tip", "skin root", "skin tip"])
plt.grid()
plt.tight_layout()
plt.show()

# L=W constraints 
plt.figure(figsize=(8,5))
plt.plot(iters, AS_point0_LequalsW_values)
plt.plot(iters, AS_point1_LequalsW_values)
plt.title("Cumprimento das constraints L=W")
plt.xlabel("Iteração")
plt.ylabel("L-W")
plt.legend(["Cruise", "Maneuver"])
plt.grid()
plt.tight_layout()
plt.show()

# CM 
plt.figure(figsize=(8,5))
plt.plot(iters, np.array(AS_point0_CM_values)[:,1])
plt.title("Pitching Moment CM")
plt.xlabel("Iteração")
plt.ylabel("CM")
plt.grid()
plt.tight_layout()
plt.show()

# Failure constraints
plt.figure(figsize=(8,5))
plt.plot(iters, AS_point1_wing_fail_values)
plt.plot(iters, AS_point1_tail_fail_values)
plt.axhline(0, color='r', linestyle='--')
plt.title("Failure constraints (wing e tail)")
plt.xlabel("Iteração")
plt.ylabel("failure")
plt.legend(["Wing", "Tail"])
plt.grid()
plt.tight_layout()
plt.show()