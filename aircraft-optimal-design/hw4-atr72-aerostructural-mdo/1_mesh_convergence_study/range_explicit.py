"""
Componente de Alcance (Breguet) para o estudo de convergência de malha
(HW4, Aircraft Optimal Design).

Esta é a versão simplificada do componente `BreguetRange` usado nos
restantes scripts do HW4 (baseline, otimização estrutural/aerodinâmica).
Nesta fase ainda não há dimensionamento estrutural (o estudo de
convergência de malha corre só a análise aerodinâmica), pelo que o termo
de massa estrutural das superfícies (`Ws`) é omitido face à versão
completa.

    R = M * a * (CL / CD) / CT * ln(1 + WF / W0)

onde:
    M   - número de Mach de cruzeiro
    a   - velocidade do som à altitude de cruzeiro [m/s]
    CT  - consumo específico de combustível, base peso [1/s]
    CL  - coeficiente de sustentação total
    CD  - coeficiente de resistência total
    W0  - peso da aeronave sem combustível (OEW + payload) [kg]
    WF  - peso de combustível queimado durante o cruzeiro [kg]

`surfaces` é aceite (e não utilizado no cálculo) apenas para manter a
mesma assinatura de chamada do `BreguetRange` completo, permitindo trocar
entre as duas versões sem alterar o resto do script.
"""
import numpy as np
import openmdao.api as om


class Range(om.ExplicitComponent):
    def initialize(self):
        self.options.declare("surfaces", types=list)

    def setup(self):
        self.add_input("CT", val=1.25e-4, units="1/s")
        self.add_input("CL", val=0.5)
        self.add_input("CD", val=0.02)
        self.add_input("speed_of_sound", val=309.6, units="m/s")
        self.add_input("WF", val=4626.0, units="kg")
        self.add_input("Mach_number", val=0.443)
        self.add_input("W0", val=13450.0, units="kg")
        self.add_output("R", val=1e6, units="m")
        self.declare_partials("*", "*", method="cs")

    def compute(self, inputs, outputs):
        CT = inputs["CT"]
        a = inputs["speed_of_sound"]
        WF = inputs["WF"]
        M = inputs["Mach_number"]
        W0 = inputs["W0"]
        outputs["R"] = M * a * inputs["CL"] / inputs["CD"] / CT * np.log(1 + WF / W0)
