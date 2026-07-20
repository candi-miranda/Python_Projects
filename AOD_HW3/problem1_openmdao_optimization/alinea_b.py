# Problem 1 b) - Himmelblau function as an OpenMDAO component.
# Generate the N2 diagram with:  openmdao n2 alinea_b.py
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


prob = om.Problem()
prob.model.add_subsystem('himmelblau', Himmelblau(), promotes=['x1', 'x2', 'f'])

prob.model.add_design_var('x1')
prob.model.add_design_var('x2')
prob.model.add_objective('f')

prob.setup()
prob.run_model()

print('f =', prob.get_val('f')[0])
