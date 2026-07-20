# Problem 1 e) - constrained optimization with the analytic derivatives from a).
import openmdao.api as om


class Himmelblau(om.ExplicitComponent):
    def setup(self):
        self.add_input('x1', val=0.0)
        self.add_input('x2', val=0.0)
        self.add_output('f', val=0.0)
        self.declare_partials('f', ['x1', 'x2'])

    def compute(self, inputs, outputs):
        x1 = inputs['x1']
        x2 = inputs['x2']
        outputs['f'] = (x1**2 + x2 - 11)**2 + (x1 + x2**2 - 7)**2

    def compute_partials(self, inputs, partials):
        x1 = inputs['x1']
        x2 = inputs['x2']
        partials['f', 'x1'] = 4*x1*(x1**2 + x2 - 11) + 2*(x1 + x2**2 - 7)
        partials['f', 'x2'] = 2*(x1**2 + x2 - 11) + 4*x2*(x1 + x2**2 - 7)


class Constraint(om.ExplicitComponent):
    def setup(self):
        self.add_input('x1', val=0.0)
        self.add_input('x2', val=0.0)
        self.add_output('g', val=0.0)
        self.declare_partials('g', ['x1', 'x2'])

    def compute(self, inputs, outputs):
        outputs['g'] = -inputs['x1'] - inputs['x2']

    def compute_partials(self, inputs, partials):
        partials['g', 'x1'] = -1.0
        partials['g', 'x2'] = -1.0


prob = om.Problem()
prob.model.add_subsystem('himmelblau', Himmelblau(), promotes=['x1', 'x2', 'f'])
prob.model.add_subsystem('con', Constraint(), promotes=['x1', 'x2', 'g'])

prob.driver = om.ScipyOptimizeDriver()
prob.driver.options['optimizer'] = 'SLSQP'
prob.driver.options['tol'] = 1e-8

prob.model.add_design_var('x1', lower=-5, upper=5)
prob.model.add_design_var('x2', lower=-5, upper=5)
prob.model.add_objective('f')
prob.model.add_constraint('g', upper=0.0)

prob.setup()
prob.set_val('x1', 0.0)
prob.set_val('x2', 0.0)
prob.run_driver()

print('x1 =', prob.get_val('x1')[0])
print('x2 =', prob.get_val('x2')[0])
print('f  =', prob.get_val('f')[0])
print('g  =', prob.get_val('g')[0])

# starting again from the optimum found above
prob.run_driver()
