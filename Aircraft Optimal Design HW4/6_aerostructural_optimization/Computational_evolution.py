import matplotlib.pyplot as plt
import openmdao.api as om
import numpy as np

# 1. Read optimization history
cr = om.CaseReader("aerostruct.db")
driver_cases = cr.get_cases('driver', recurse=False)

# 2. Lists to store history
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

# 3. Extract values from each iteration 
for case in driver_cases:
    # Objective
    range_values.append(case['RangeCalc.Range']/1000)

    # Trim
    alpha_values.append(case['alpha'])
    alpha_maneuver_values.append(case['alpha_maneuver'])

    # Twist
    wing_twist_values.append(case['wing.twist_cp'])
    tail_twist_values.append(case['tail.twist_cp'])

    # Geometry
    wing_span_values.append(case['wing.geometry.span'])
    tail_span_values.append(case['tail.geometry.span'])
    wing_sweep_values.append(case['wing.sweep'])

    # Structure
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
plt.title("Range over iterations")
plt.xlabel("Iteration")
plt.ylabel("Range [km]")
plt.grid()
plt.tight_layout()
plt.show()

# Trim 
plt.figure(figsize=(8,5))
plt.plot(iters, alpha_values)
plt.plot(iters, alpha_maneuver_values)
plt.title("Angles of attack evolution")
plt.xlabel("Iteration")
plt.ylabel("Angles [deg]")
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
plt.title("Wing and tail twist")
plt.xlabel("Iteration")
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
plt.title("Wing structural thicknesses")
plt.xlabel("Iteration")
plt.ylabel("Thickness [m]")
plt.legend(["spar root", "spar tip", "skin root", "skin tip"])
plt.grid()
plt.tight_layout()
plt.show()

# L=W constraints 
plt.figure(figsize=(8,5))
plt.plot(iters, AS_point0_LequalsW_values)
plt.plot(iters, AS_point1_LequalsW_values)
plt.title("L=W constraints compliance")
plt.xlabel("Iteration")
plt.ylabel("L-W")
plt.legend(["Cruise", "Maneuver"])
plt.grid()
plt.tight_layout()
plt.show()

# CM 
plt.figure(figsize=(8,5))
plt.plot(iters, np.array(AS_point0_CM_values)[:,1])
plt.title("Pitching Moment CM")
plt.xlabel("Iteration")
plt.ylabel("CM")
plt.grid()
plt.tight_layout()
plt.show()

# Failure constraints
plt.figure(figsize=(8,5))
plt.plot(iters, AS_point1_wing_fail_values)
plt.plot(iters, AS_point1_tail_fail_values)
plt.axhline(0, color='r', linestyle='--')
plt.title("Failure constraints (wing and tail)")
plt.xlabel("Iteration")
plt.ylabel("failure")
plt.legend(["Wing", "Tail"])
plt.grid()
plt.tight_layout()
plt.show()
