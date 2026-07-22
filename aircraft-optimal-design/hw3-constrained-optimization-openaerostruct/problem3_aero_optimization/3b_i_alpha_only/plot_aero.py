# -*- coding: utf-8 -*-
"""
 Suplemental script to visualize optimization history of example in
 https://mdolab-openaerostruct.readthedocs-hosted.com/en/latest/aero_walkthrough.html
"""
import matplotlib.pyplot as plt
import openmdao.api as om
import numpy as np

# Instantiate your CaseReader
cr = om.CaseReader("aero.db")

# Get driver cases (do not recurse to system/solver cases)
driver_cases = cr.get_cases('driver', recurse=False)

# Plot the path the design variables took to convergence
# Note that there are five lines in the left plot because "wing.twist_cp"
# contains five variables that are being optimized
var_values = []
con_values = []
obj_values = []
twist_values = []

for case in driver_cases:
    var_values.append(case['alpha'])
    con_values.append(case['aero_point_0.wing_perf.CL'])
    obj_values.append(case['aero_point_0.wing_perf.CD'])
    twist_values.append(case['wing.twist_cp'])

#fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(16,4))

fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.5, hspace=None)

fig.suptitle('Sample of possible variable/function optimization history visualization', fontsize=16)

ax1.plot(np.arange(len(var_values)), np.array(var_values))
ax1.set(xlabel='Iterations', ylabel='alpha')
ax1.legend(['alpha'])
ax1.grid()

ax2.plot(np.arange(len(con_values)), np.array(con_values))
ax2.set(xlabel='Iterations', ylabel='Constraint')
ax2.legend(['CL'])
ax2.grid()

ax3.plot(np.arange(len(obj_values)), np.array(obj_values))
ax3.set(xlabel='Iterations', ylabel='Objective function')
ax3.legend(['CD'])
ax3.grid()



twist_values = np.array(twist_values)

ax4.plot(np.arange(len(twist_values)), twist_values[:,1], label="twist_cp1")
ax4.plot(np.arange(len(twist_values)), twist_values[:,2], label="twist_cp2")
ax4.plot(np.arange(len(twist_values)), twist_values[:,3], label="twist_cp3")

ax4.set(xlabel='Iterations', ylabel='Twist [deg]', title='Twist CP history')
ax4.legend()
ax4.grid()


plt.show()