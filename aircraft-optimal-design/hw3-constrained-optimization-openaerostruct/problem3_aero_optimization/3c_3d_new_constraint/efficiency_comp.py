"""
Componente de Eficiência Aerodinâmica (HW3, Aircraft Optimal Design,
Problema 3(c)/3(d)).

Calcula a fineza aerodinâmica (razão sustentação/resistência):

    eff = CL / CD

Usado como restrição adicional (eff >= 24) na otimização de forma da asa
já construída no Problema 3(b), sem alterar o resto do modelo.
"""
import openmdao.api as om


class AeroEfficiency(om.ExplicitComponent):
    def setup(self):
        self.add_input("CL", val=0.5)
        self.add_input("CD", val=0.02)
        self.add_output("eff", val=25.0)

        self.declare_partials("eff", ["CL", "CD"])

    def compute(self, inputs, outputs):
        outputs["eff"] = inputs["CL"] / inputs["CD"]

    def compute_partials(self, inputs, partials):
        CL = inputs["CL"]
        CD = inputs["CD"]
        partials["eff", "CL"] = 1.0 / CD
        partials["eff", "CD"] = -CL / CD**2
