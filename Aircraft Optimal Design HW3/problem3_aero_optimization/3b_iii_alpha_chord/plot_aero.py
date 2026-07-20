# -*- coding: utf-8 -*-
import os
import matplotlib.pyplot as plt
import openmdao.api as om
import numpy as np

# Mapeamento dos ficheiros .db existentes na tua pasta (ajustados para a tua convenção)
casos = {
    "aero_linear.db": "Linear",
    "aero_elliptic.db": "Eliptico",
    "aero_quadratic.db": "Quadratico"
}

for db_file, nome_caso in casos.items():
    if not os.path.exists(db_file):
        print(f"Aviso: {db_file} não encontrado. Salta para o próximo.")
        continue
        
    print(f"A processar histórico do Caso: {nome_caso} ({db_file})...")
    
    cr = om.CaseReader(db_file)
    driver_cases = cr.get_cases('driver', recurse=False)

    chord_history = []
    con_values = []
    obj_values = []
    alpha_values = []
    
    for case in driver_cases:
        alpha_values.append(case['alpha'])
        con_values.append(case['aero_point_0.wing_perf.CL'])
        obj_values.append(case['aero_point_0.wing_perf.CD'])
        chord_history.append(case['wing.chord_cp'])

    iterations = np.arange(len(alpha_values))
    chord_history = np.array(chord_history) # Formato: [Iterações, num_control_points]
    num_cp = chord_history.shape[1]

    # =============================================================================
    # FIGURA 1: Variáveis de Design (Evolução das Cordas de Controlo e Alpha)
    # =============================================================================
    fig1, (ax_chord, ax_alpha) = plt.subplots(1, 2, figsize=(10, 4))
    fig1.suptitle(f'Histórico de Otimização: Variáveis de Design ({nome_caso})', fontsize=12, fontweight='bold')

    # Subplot 1: Evolução temporal de cada ponto de controlo da corda
    for i in range(num_cp):
        # Mapeamento de nomes lógicos para a legenda dependendo de quantos pontos existem
        if i == 0:
            label_cp = "Chord Ponta (CP 1)" if chord_history[0,0] < chord_history[0,-1] else "Chord Raiz (CP 1)"
        elif i == num_cp - 1:
            label_cp = "Chord Raiz (CP Final)" if chord_history[0,0] < chord_history[0,-1] else "Chord Ponta (CP Final)"
        else:
            label_cp = f"Chord Mid (CP {i+1})"
            
        ax_chord.plot(iterations, chord_history[:, i], linewidth=2, label=label_cp)
        
    ax_chord.set(xlabel='Iterations', ylabel='Chord control points (m)')
    ax_chord.legend(loc='best')
    ax_chord.grid(True)

    # Subplot 2: Evolução temporal do Alpha
    ax_alpha.plot(iterations, np.array(alpha_values), color='tab:orange', linewidth=2)
    ax_alpha.set(xlabel='Iterations', ylabel='alpha (deg)')
    ax_alpha.legend(['alpha'], loc='best')
    ax_alpha.grid(True)

    fig1.tight_layout()
    fig1.savefig(f"history_variables_{nome_caso.lower()}.png", dpi=300)
    plt.close(fig1)

    # =============================================================================
    # FIGURA 2: Performance Aerodinâmica (CD e CL)
    # =============================================================================
    fig2, (ax_cd, ax_cl) = plt.subplots(1, 2, figsize=(10, 4))
    fig2.suptitle(f'Histórico de Otimização: Performance Aerodinâmica ({nome_caso})', fontsize=12, fontweight='bold')

    ax_cd.plot(iterations, np.array(obj_values), color='tab:purple', linewidth=2)
    ax_cd.set(xlabel='Iterations', ylabel='Objective function (CD)')
    ax_cd.legend(['CD'], loc='best')
    ax_cd.grid(True)

    ax_cl.plot(iterations, np.array(con_values), color='tab:green', linewidth=2)
    ax_cl.set(xlabel='Iterations', ylabel='Constraint (CL)')
    ax_cl.legend(['CL'], loc='best')
    ax_cl.grid(True)

    fig2.tight_layout()
    fig2.savefig(f"history_performance_{nome_caso.lower()}.png", dpi=300)
    plt.close(fig2)

print("\nProcessamento concluído com sucesso! Os gráficos de variáveis agora mostram a evolução das cordas.")