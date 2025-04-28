import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use('TkAgg')
from mppt_simulator import run_simulation, plot_simulation_results, PVPanel
import matplotlib.pyplot as plt

class MPPT_GUI:
    def __init__(self, master):
        self.master = master
        self.irrad_var = tk.DoubleVar(value=1000)
        self.temp_var = tk.IntVar(value=25)
        self.step_var = tk.DoubleVar(value=0.1)
        self.status_var = tk.StringVar(value="就绪")
        self.voltages, self.currents, self.powers = [], [], []
        master.title("MPPT 仿真控制台")
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 功能按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")
        ttk.Button(btn_frame, text="显示光伏特性曲线", command=self.show_pv_curve).grid(row=0, column=0, pady=5)
        ttk.Button(btn_frame, text="显示MPPT仿真结果", command=self.run_and_plot_simulation).grid(row=1, column=0, pady=5)
        ttk.Button(btn_frame, text="退出程序", command=self.cleanup_exit).grid(row=2, column=0, pady=15)

        # 参数调节面板
        param_frame = ttk.LabelFrame(main_frame, text="动态参数调节", padding=10)
        param_frame.grid(row=0, column=1, padx=10, sticky="n")
        ttk.Label(param_frame, text="辐照度 (W/m²):").grid(row=0, column=0, sticky="w")
        ttk.Scale(param_frame, from_=200, to=1200, variable=self.irrad_var, command=lambda v: self.on_parameters_updated()).grid(row=0, column=1, padx=5)
        ttk.Label(param_frame, textvariable=self.irrad_var).grid(row=0, column=2)
        ttk.Label(param_frame, text="温度 (°C):").grid(row=1, column=0, sticky="w")
        ttk.Scale(param_frame, from_=0, to=50, variable=self.temp_var, command=lambda v: self.on_parameters_updated()).grid(row=1, column=1, padx=5)
        ttk.Label(param_frame, textvariable=self.temp_var).grid(row=1, column=2)
        ttk.Label(param_frame, text="步长 (V):").grid(row=2, column=0, sticky="w")
        ttk.Scale(param_frame, from_=0.05, to=1.0, variable=self.step_var, command=lambda v: self.on_parameters_updated()).grid(row=2, column=1, padx=5)
        ttk.Label(param_frame, textvariable=self.step_var).grid(row=2, column=2)

        # 状态栏
        ttk.Label(main_frame, textvariable=self.status_var, relief="sunken", anchor="w").grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)

    def on_parameters_updated(self, *args):
        try:
            params = {
                "irrad": self.irrad_var.get(),
                "temp": self.temp_var.get(),
                "step_size": self.step_var.get()
            }
            self.voltages, self.currents, self.powers = run_simulation(**params)
            self.status_var.set(f"参数已更新: 辐照度={params['irrad']}W/m², 温度={params['temp']}°C, 步长={params['step_size']}V")
            if hasattr(self, 'results_window'):
                self.plot_simulation_results()
        except Exception as e:
            self.status_var.set(f"错误: {str(e)}")

    def run_and_plot_simulation(self):
        params = {
            "irrad": self.irrad_var.get(),
            "temp": self.temp_var.get(),
            "step_size": self.step_var.get()
        }
        self.voltages, self.currents, self.powers = run_simulation(**params)
        self.plot_simulation_results()

    def plot_simulation_results(self):
        plt.close("MPPT Simulation Results")
        plt.figure("MPPT Simulation Results", figsize=(10,6))
        plt.subplot(3,1,1)
        plt.plot(self.voltages, 'b-'), plt.ylabel('Voltage (V)'), plt.grid(True)
        plt.subplot(3,1,2)
        plt.plot(self.currents, 'r-'), plt.ylabel('Current (A)'), plt.grid(True)
        plt.subplot(3,1,3)
        plt.plot(self.powers, 'g-'), plt.ylabel('Power (W)'), plt.xlabel('Iterations'), plt.grid(True)
        plt.tight_layout()
        plt.show(block=False)

    def show_pv_curve(self):
        PVPanel.plot_characteristics()

    def cleanup_exit(self):
        plt.close('all')
        self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = MPPT_GUI(root)
    root.mainloop()