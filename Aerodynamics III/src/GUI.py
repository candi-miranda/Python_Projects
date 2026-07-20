import tkinter as tk
from tkinter import ttk, messagebox
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from Task1 import solve_steady_state
from Task2 import run_transient


class AeroSolverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aero III - Nozzle & Rayleigh Pipe Solver")
        self.root.geometry("1600x1100")

        self.gamma = tk.DoubleVar(value=1.4)
        self.R = tk.DoubleVar(value=287.05)
        self.P01 = tk.DoubleVar(value=1000000)  # Pa
        self.P02 = tk.DoubleVar(value=101325)   # Pa
        self.T0 = tk.DoubleVar(value=300)       # K
        self.A_throat = tk.DoubleVar(value=0.01)  # m2
        self.A_pipe = tk.DoubleVar(value=0.02)  # m2
        self.L = tk.DoubleVar(value=1.0)   # m
        self.q_rate = tk.DoubleVar(value=0.0)  # W/m
        self.timestep_type = tk.StringVar(value="Variavel")  
        self.dt_input = tk.DoubleVar(value=100) 
        self.V = tk.DoubleVar(value=10.0)       # m3 

        self.setup_ui()

 
    PRESETS = {
        "— Select preset —": None,
        # Task 1 (Steady-State) 
        "T1: Subsonic (unchoked)": dict(
            gamma=1.4, R=287.05, P01=300000, P02=299000, T0=300,
            A_throat=0.01, A_pipe=0.05, L=1.0, q_rate=0, V=10),
        "T1: Choked subsonic (shock at throat)": dict(
            gamma=1.4, R=287.05, P01=300000, P02=297150, T0=300,
            A_throat=0.01, A_pipe=0.05, L=1.0, q_rate=0, V=10),
        "T1: Normal shock inside nozzle": dict(
            gamma=1.4, R=287.05, P01=300000, P02=150000, T0=300,
            A_throat=0.01, A_pipe=0.05, L=1.0, q_rate=0, V=10),
        "T1: Shock at nozzle exit": dict(
            gamma=1.4, R=287.05, P01=300000, P02=73025, T0=300,
            A_throat=0.01, A_pipe=0.05, L=1.0, q_rate=0, V=10),
        "T1: Fully supersonic (overexpanded)": dict(
            gamma=1.4, R=287.05, P01=300000, P02=5000, T0=300,
            A_throat=0.01, A_pipe=0.05, L=1.0, q_rate=0, V=10),
        "T1: Rayleigh heating (subsonic pipe)": dict(
            gamma=1.4, R=287.05, P01=300000, P02=150000, T0=300,
            A_throat=0.01, A_pipe=0.05, L=1.0, q_rate=400000, V=10),
        "T1: Rayleigh heating (supersonic pipe)": dict(
            gamma=1.4, R=287.05, P01=300000, P02=5000, T0=300,
            A_throat=0.01, A_pipe=0.05, L=1.0, q_rate=400000, V=10),
        "T1: Thermal choking (supersonic)": dict(
            gamma=1.4, R=287.05, P01=300000, P02=5000, T0=300,
            A_throat=0.01, A_pipe=0.05, L=1.0, q_rate=1600000, V=10),
        "T1: Thermal choking (subsonic)": dict(
            gamma=1.4, R=287.05, P01=300000, P02=50000, T0=300,
            A_throat=0.01, A_pipe=0.05, L=1.0, q_rate=3600000, V=10),
        "T1: Rayleigh cooling (supersonic pipe)": dict(
            gamma=1.4, R=287.05, P01=300000, P02=5000, T0=300,
            A_throat=0.01, A_pipe=0.05, L=1.0, q_rate=-240000, V=10),
        "T1: Rayleigh cooling (subsonic pipe)": dict(
            gamma=1.4, R=287.05, P01=300000, P02=50000, T0=300,
            A_throat=0.01, A_pipe=0.10, L=1.0, q_rate=-1120000, V=10),
        # Task 2 (Transient)
        "T2: Blowdown supersonic → subsonic": dict(
            gamma=1.4, R=287.05, P01=300000, P02=5000, T0=300,
            A_throat=0.01, A_pipe=0.05, L=1.0, q_rate=0, V=10),
        "T2: Blowdown with strong Rayleigh heating": dict(
            gamma=1.4, R=287.05, P01=300000, P02=5000, T0=300,
            A_throat=0.01, A_pipe=0.05, L=1.0, q_rate=400000, V=1000),
        "T2: Near-equal pressures (subsonic decay)": dict(
            gamma=1.4, R=287.05, P01=300000, P02=298000, T0=300,
            A_throat=0.01, A_pipe=0.05, L=1.0, q_rate=0, V=10000),
        "T2: Large reservoir blowdown": dict(
            gamma=1.4, R=287.05, P01=300000, P02=5000, T0=300,
            A_throat=0.01, A_pipe=0.05, L=1.0, q_rate=0, V=1000),
        "T2: Fast blowdown (V=10, choked)": dict(
            gamma=1.4, R=287.05, P01=300000, P02=5000, T0=300,
            A_throat=0.01, A_pipe=0.05, L=1.0, q_rate=0, V=10),
        "T2: Blowdown with supersonic cooling (fast)": dict(
            gamma=1.4, R=287.05, P01=300000, P02=5000, T0=300,
            A_throat=0.01, A_pipe=0.05, L=1.0, q_rate=-240000, V=10),
        "T2: Blowdown with supersonic cooling (slow)": dict(
            gamma=1.4, R=287.05, P01=300000, P02=5000, T0=300,
            A_throat=0.01, A_pipe=0.05, L=1.0, q_rate=-240000, V=1000),
    }

    def _apply_preset(self, event=None):
        name = self.preset_var.get()
        p = self.PRESETS.get(name)
        if p is None:
            return
        self.gamma.set(p['gamma'])
        self.R.set(p['R'])
        self.P01.set(p['P01'])
        self.P02.set(p['P02'])
        self.T0.set(p['T0'])
        self.A_throat.set(p['A_throat'])
        self.A_pipe.set(p['A_pipe'])
        self.L.set(p['L'])
        self.q_rate.set(p['q_rate'])
        self.V.set(p['V'])
        self.status_var.set(p.get('note', ''))

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        input_frame = ttk.LabelFrame(main_frame, text="Input Parameters", padding="10")
        input_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        ttk.Label(input_frame, text="Preset cases:", font=("", 9, "bold")).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 2))
        self.preset_var = tk.StringVar(value="— Select preset —")
        preset_cb = ttk.Combobox(
            input_frame, textvariable=self.preset_var,
            values=list(self.PRESETS.keys()), state="readonly", width=26)
        preset_cb.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 8))
        preset_cb.bind("<<ComboboxSelected>>", self._apply_preset)

        ttk.Separator(input_frame, orient="horizontal").grid(
            row=2, column=0, columnspan=2, sticky=tk.EW, pady=4)

        params = [
            ("Gamma (γ):",               self.gamma),
            ("R (J/kg·K):",              self.R),
            ("P0,1 (Pa):",               self.P01),
            ("P0,2 (Pa):",               self.P02),
            ("T0 (K):",                  self.T0),
            ("A_throat (m²):",           self.A_throat), 
            ("A_pipe (m²):",             self.A_pipe),
            ("Pipe length L (m):",       self.L),
            ("Heat flux q' (W/m):",     self.q_rate),
            ("Reservoir volume V (m³):", self.V),
        ]

        row_offset = 3   
        for i, (label, var) in enumerate(params):
            ttk.Label(input_frame, text=label).grid(row=row_offset+i, column=0, sticky=tk.W, pady=2)
            ttk.Entry(input_frame, textvariable=var, width=15).grid(row=row_offset+i, column=1, pady=2)

        row_idx = row_offset + len(params)

        ttk.Label(input_frame, text="Perfil do Bocal:").grid(
            row=row_idx, column=0, sticky=tk.W, pady=5)
        self.nozzle_profile = ttk.Combobox(
            input_frame, values=["Sinusoidal", "Polinomial"], state="readonly", width=13)
        self.nozzle_profile.current(0)
        self.nozzle_profile.grid(row=row_idx, column=1, pady=5)
        row_idx += 1

        ttk.Label(input_frame, text="Tipo de Timestep:").grid(
            row=row_idx, column=0, sticky=tk.W, pady=5)
        
        ttk.Radiobutton(input_frame, text="Variável",
                        variable=self.timestep_type, value="Variavel",
                        command=self.toggle_timestep_entry).grid(
            row=row_idx, column=1, sticky=tk.W)
        row_idx += 1
        ttk.Radiobutton(input_frame, text="Input do Utilizador",
                        variable=self.timestep_type, value="Fixo",
                        command=self.toggle_timestep_entry).grid(
            row=row_idx, column=1, sticky=tk.W)
        row_idx += 1

        ttk.Label(input_frame, text="Valor Timestep (s):").grid(
            row=row_idx, column=0, sticky=tk.W, pady=2)
        self.dt_entry = ttk.Entry(input_frame, textvariable=self.dt_input,
                                  width=15, state="disabled")
        self.dt_entry.grid(row=row_idx, column=1, pady=2)
        row_idx += 1

        ttk.Button(input_frame, text="Executar Tarefa 1 (Steady)",
                   command=self.run_task_1).grid(
            row=row_idx, column=0, columnspan=2, sticky=tk.EW, pady=10)
        row_idx += 1
        ttk.Button(input_frame, text="Executar Tarefa 2 (Transient)",
                   command=self.run_task_2).grid(
            row=row_idx, column=0, columnspan=2, sticky=tk.EW, pady=5)
        row_idx += 1

        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(input_frame, textvariable=self.status_var, foreground="blue",
                  wraplength=200).grid(row=row_idx, column=0, columnspan=2, pady=8)

        self.plot_frame = ttk.LabelFrame(main_frame, text="Resultados e Gráficos", padding="10")
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        self.fig, self.axes = plt.subplots(3, 3, figsize=(11, 8))
        self.fig.tight_layout(pad=3.0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def toggle_timestep_entry(self):
        state = "disabled" if self.timestep_type.get() == "Variavel" else "normal"
        self.dt_entry.config(state=state)

    def _get_profile(self):
        return {"Sinusoidal": "sinusoidal", "Polinomial": "quadratic"}.get(
            self.nozzle_profile.get(), "sinusoidal")

    def validate_inputs(self):
        try:
            if self.gamma.get() <= 1.0:
                raise ValueError("γ > 1.")
            if self.R.get() <= 0:
                raise ValueError("R  > 0.")
            if self.A_throat.get() >= self.A_pipe.get():
                raise ValueError("A_throat < que A_pipe.")
            if self.P01.get() <= self.P02.get():
                raise ValueError("P0,1 > P0,2.")
            if self.T0.get() <= 0:
                raise ValueError("T0 > 0.")
            return True
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return False

    def run_task_1(self):
        if not self.validate_inputs():
            return
        self.status_var.set("Running Task 1...")
        self.root.update()
        try:
            result = solve_steady_state(
                gamma    = self.gamma.get(),
                R        = self.R.get(),
                P01      = self.P01.get(),
                P02      = self.P02.get(),
                T0       = self.T0.get(),
                A_throat = self.A_throat.get(),
                A_pipe   = self.A_pipe.get(),
                L        = self.L.get(),
                q_rate   = self.q_rate.get(),
                profile  = self._get_profile(),
            )
            self._plot_task1(result)
            shock_str = f"  |  NSW @ x={result['x_shock']:.3f} m" if result['x_shock'] else ""
            choke_str  = "  |  ⚠ thermal choking in pipe" if result.get('thermally_choked') else ""
            self.status_var.set(
                f"Task 1 done.  ṁ = {result['mdot']:.4f} kg/s"
                f"  |  regime: {result['regime']}{shock_str}{choke_str}")
        except Exception as e:
            messagebox.showerror("Solver Error", str(e))
            self.status_var.set("Task 1 failed.")
    
    def run_task_2(self):
        if not self.validate_inputs():
            return

        gamma  = self.gamma.get()
        R      = self.R.get()
        T0     = self.T0.get()
        V      = self.V.get()
        P01_0  = self.P01.get()
        P02_0  = self.P02.get()
        A_th   = self.A_throat.get()
        C_choked = A_th * np.sqrt(gamma / (R * T0)) * (2 / (gamma + 1)) ** ((gamma + 1) / (2 * (gamma - 1)))
        P_eq = (P01_0 + P02_0) / 2.0
        if P_eq > 0 and P01_0 > P_eq:
            t_est = (V / (R * T0)) / C_choked * np.log(P01_0 / P_eq)
        else:
            t_est = float('inf')

        A_pipe = self.A_pipe.get()
        L      = self.L.get()
        V_flow = A_pipe * L   
        qs_ratio = V / V_flow
        if qs_ratio < 20:
            qs_warn = f"  V/V_pipe={qs_ratio:.1f} < 20: quasi-steady may be inaccurate."
        else:
            qs_warn = ""
        est_msg = f"Estimated t_final ≈ {t_est:.1f} s (choked approx).{qs_warn}  Running..."
        self.status_var.set(est_msg)
        self.root.update()
        dt_fixed = None if self.timestep_type.get() == "Variavel" else self.dt_input.get()

        def _worker():
            try:
                hist = run_transient(
                    gamma              = self.gamma.get(),
                    R                  = self.R.get(),
                    T0                 = self.T0.get(),
                    V                  = self.V.get(),
                    P01_init           = self.P01.get(),
                    P02_init           = self.P02.get(),
                    A_throat           = self.A_throat.get(),
                    A_pipe             = self.A_pipe.get(),
                    L                  = self.L.get(),
                    q_rate             = self.q_rate.get(),
                    solve_steady_state = solve_steady_state,
                    dt_fixed           = dt_fixed,
                    profile            = self._get_profile(),
                )
                
                self.root.after(0, lambda: self._task2_done(hist))
            except Exception as e:
                self.root.after(0, lambda: self._task2_error(str(e)))

        threading.Thread(target=_worker, daemon=True).start()

    def _task2_done(self, hist):
        self._plot_task2(hist)
        self.status_var.set(f"Task 2 done.  t_final = {hist['t'][-1]:.1f} s")

    def _task2_error(self, msg):
        messagebox.showerror("Solver Error", msg)
        self.status_var.set("Task 2 failed.")

    def _plot_task1(self, r):
        for ax in self.axes.flat:
            ax.clear()

        x   = r['x']
        L_n = r['L_n']
        th  = x[r['stations']['throat']]
        ne  = x[r['stations']['nozzle_out']]

        plots = [
            (self.axes[0, 0], r['M'],       'Mach Number',            'M [-]'),
            (self.axes[0, 1], r['P']/1e3,   'Static Pressure',        'P [kPa]'),
            (self.axes[0, 2], r['P0x']/1e3, 'Stagnation Pressure',    'P0 [kPa]'),
            (self.axes[1, 0], r['T'],        'Static Temperature',     'T [K]'),
            (self.axes[1, 1], r['T0x'],      'Stagnation Temperature', 'T0 [K]'),
            (self.axes[1, 2], r['s'],        'Entropy Change',         'Δs [J/kg·K]'),
        ]

        for ax, y, title, ylabel in plots:
            ax.plot(x, y, 'b-', linewidth=1.5)
            ax.set_title(title, fontsize=9)
            ax.set_xlabel('x [m]', fontsize=8)
            ax.set_ylabel(ylabel, fontsize=8)
            ax.grid(True, alpha=0.3)
            ax.yaxis.get_major_formatter().set_useOffset(False)
            ax.axvline(ne, color='gray',   linestyle='--', linewidth=0.8, label='Nozzle exit')
            ax.axvline(th, color='red',    linestyle=':',  linewidth=0.8, label='Throat')
            if r['x_shock'] is not None:
                ax.axvline(r['x_shock'], color='orange', linestyle='-',
                           linewidth=1.2, label='NSW')

        ax = self.axes[2, 0]
        ax.plot(x, np.full_like(x, r['mdot']), 'k-', linewidth=1.5)
        ax.set_title('Mass Flow Rate', fontsize=9)
        ax.set_xlabel('x [m]', fontsize=8)
        ax.set_ylabel('ṁ [kg/s]', fontsize=8)
        ax.grid(True, alpha=0.3)

        from Task1 import area as get_area_func
        A_func   = get_area_func(self._get_profile())
        A_throat = self.A_throat.get()
        A_pipe   = self.A_pipe.get()
        L_n      = r['L_n']
        L        = self.L.get()
        x_geom = np.linspace(0, L_n + L, 500)
        A_x    = np.array([A_func(xi, A_throat, A_pipe, L_n, L) for xi in x_geom])
        half_h = np.sqrt(A_x / np.pi)

        ax = self.axes[2, 1]
        ax.fill_between(x_geom,  half_h, -half_h, color='lightsteelblue', alpha=0.5) 
        ax.plot(x_geom,  half_h, 'b-', linewidth=1.5)  
        ax.plot(x_geom, -half_h, 'b-', linewidth=1.5)  
        ax.axhline(0, color='gray', linestyle=':', linewidth=0.6)
        ax.axvline(ne, color='gray',  linestyle='--', linewidth=0.8, label='Nozzle exit')
        ax.axvline(th, color='red',   linestyle=':',  linewidth=0.8, label='Throat')
        if r['x_shock'] is not None:
            ax.axvline(r['x_shock'], color='orange', linestyle='-', linewidth=1.2, label='NSW')
        ax.set_title('Geometry', fontsize=9)
        ax.set_xlabel('x [m]', fontsize=8)
        ax.set_ylabel('r [m]', fontsize=8)
        r_pipe = np.sqrt(A_pipe / np.pi)
        ax.set_ylim(-1.1 * r_pipe, 1.1 * r_pipe)
        ax.grid(True, alpha=0.3)

        ax = self.axes[2, 2]
        ax.axis('off')
        legend_items = [
            (dict(color='red',    linestyle=':',  linewidth=1.5), 'Throat (M = 1)'),
            (dict(color='gray',   linestyle='--', linewidth=1.5), 'Nozzle exit'),
            (dict(color='orange', linestyle='-',  linewidth=1.5), 'Normal shock (NSW)'),
        ]
        handles = [plt.Line2D([0], [0], **style) for style, _ in legend_items]
        labels  = [label for _, label in legend_items]
        ax.legend(handles, labels, loc='center', fontsize=9,
                  frameon=True, title='Vertical lines', title_fontsize=9)
        self.fig.tight_layout(pad=2.5)
        self.canvas.draw()


    def _plot_task2(self, hist):
        for ax in self.axes.flat:
            ax.clear()

        t = hist['t']

        ax = self.axes[0, 0]
        ax.plot(t, hist['P01']/1e3, 'b-', label='P0,1')
        ax.plot(t, hist['P02']/1e3, 'r-', label='P0,2')
        ax.set_title('Reservoir Pressures', fontsize=9)
        ax.set_xlabel('t [s]', fontsize=8)
        ax.set_ylabel('P0 [kPa]', fontsize=8)
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

        ax = self.axes[0, 1]
        ax.plot(t, hist['mdot'], 'k-')
        ax.set_title('Mass Flow Rate', fontsize=9)
        ax.set_xlabel('t [s]', fontsize=8)
        ax.set_ylabel('ṁ [kg/s]', fontsize=8)
        ax.grid(True, alpha=0.3)

        colors = {
            'nozzle_in':          ('green',  'nozzle in'),
            'throat':             ('red',    'throat'),
            'nozzle_out/pipe_in': ('blue',   'nozzle out / pipe in'),
            'pipe_out':           ('orange', 'pipe out'),
        }
        def _smooth(arr, k=5):
            from scipy.ndimage import median_filter
            valid = np.array(arr, dtype=float)
            mask  = ~np.isnan(valid)
            if mask.sum() < k:
                return valid
            valid[mask] = median_filter(valid[mask], size=k, mode='nearest')
            return valid

        for ax, data, title, ylabel in [
            (self.axes[1, 0], hist['station_M'], 'Mach at Stations',        'M [-]'),
            (self.axes[1, 1], hist['station_T'], 'Temperature at Stations', 'T [K]'),
            (self.axes[1, 2], hist['station_P'], 'Pressure at Stations',    'P [Pa]'),
        ]:
            for station, (color, label) in colors.items():
                if station in data:
                    y = _smooth(data[station])
                    ax.plot(t, y, color=color, label=label, linewidth=1.2)
            ax.set_title(title, fontsize=9)
            ax.set_xlabel('t [s]', fontsize=8)
            ax.set_ylabel(ylabel, fontsize=8)
            ax.legend(fontsize=7)
            ax.grid(True, alpha=0.3)

        for ax in [self.axes[0, 2], self.axes[2, 0], self.axes[2, 1], self.axes[2, 2]]:
            ax.axis('off')

        self.fig.tight_layout(pad=2.5)
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = AeroSolverApp(root)
    root.mainloop()