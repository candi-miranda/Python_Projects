# Problem 1 c) - unconstrained optimization with SLSQP, finite-difference derivatives.
import openmdao.api as om


class Himmelblau(om.ExplicitComponent):
    def setup(self):
        self.add_input('x1', val=0.0)
        self.add_input('x2', val=0.0)
        self.add_output('f', val=0.0)
        self.declare_partials('f', ['x1', 'x2'], method='fd', step=1e-6, form='forward')

    def compute(self, inputs, outputs):
        x1 = inputs['x1']
        x2 = inputs['x2']
        outputs['f'] = (x1**2 + x2 - 11)**2 + (x1 + x2**2 - 7)**2


prob = om.Problem()
prob.model.add_subsystem('himmelblau', Himmelblau(), promotes=['x1', 'x2', 'f'])

prob.driver = om.ScipyOptimizeDriver()
prob.driver.options['optimizer'] = 'SLSQP'
prob.driver.options['tol'] = 1e-8

prob.model.add_design_var('x1', lower=-5, upper=5)
prob.model.add_design_var('x2', lower=-5, upper=5)
prob.model.add_objective('f')

prob.setup()
prob.set_val('x1', 0.0)
prob.set_val('x2', 0.0)
prob.run_driver()

print('x1 =', prob.get_val('x1')[0])
print('x2 =', prob.get_val('x2')[0])
print('f  =', prob.get_val('f')[0])
