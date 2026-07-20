# -*- coding: utf-8 -*-
"""
 Suplemental script to visualize optimization history of example in
 https://mdolab-openaerostruct.readthedocs-hosted.com/en/latest/aero_walkthrough.html
"""
import matplotlib.pyplot as plt
import openmdao.api as om
import numpy as np

# Instantiate your CaseReader
cr = om.CaseReader("aero_linear_total.db")

# Get driver cases (do not recurse to system/solver cases)
driver_cases = cr.get_cases('driver', recurse=False)

# Plot the path the design variables took to convergence
# Note that there are five lines in the left plot because "wing.twist_cp"
# contains five variables that are being optimized
var_values = []
con_values = []
obj_values = []
alpha_values = []
for case in driver_cases:
    alpha_values.append(case['alpha'])
    var_values.append(case['wing.twist_cp'])
    con_values.append(case['aero_point_0.wing_perf.CL'])
    obj_values.append(case['aero_point_0.wing_perf.CD'])

# =============================================================================
# BLOCO DE GERAÇÃO: 2 FIGURAS COM 2 GRÁFICOS CADA
# =============================================================================
iterations = np.arange(len(var_values))

# FIGURA 1: Variáveis de Design (Torções e Alpha)
fig1, (ax_gamma, ax_alpha) = plt.subplots(1, 2, figsize=(10, 4))

ax_gamma.plot(iterations, np.array(var_values), linewidth=2)
ax_gamma.set(xlabel='Iterations', ylabel='gamma')
ax_gamma.legend(['gamma1', 'gamma2', 'gamma3', 'gamma4'], loc='best')
ax_gamma.grid(True)

ax_alpha.plot(iterations, np.array(alpha_values), color='tab:orange', linewidth=2)
ax_alpha.set(xlabel='Iterations', ylabel='alpha')
ax_alpha.legend(['alpha'], loc='best')
ax_alpha.grid(True)

fig1.tight_layout()
fig1.savefig("history_variables.png", dpi=300)

# FIGURA 2: Performance Aerodinâmica (CD e CL)
fig2, (ax_cd, ax_cl) = plt.subplots(1, 2, figsize=(10, 4))

ax_cd.plot(iterations, np.array(obj_values), color='tab:purple', linewidth=2)
ax_cd.set(xlabel='Iterations', ylabel='Objective function (CD)')
ax_cd.legend(['CD'], loc='best')
ax_cd.grid(True)

ax_cl.plot(iterations, np.array(con_values), color='tab:green', linewidth=2)
ax_cl.set(xlabel='Iterations', ylabel='Constraint (CL)')
ax_cl.legend(['CL'], loc='best')
ax_cl.grid(True)

fig2.tight_layout()
fig2.savefig("history_performance.png", dpi=300)

plt.show()