# mppt_gui.py
import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use('TkAgg')
from mppt_simulator import PVPanel, run_simulation, plot_simulation_results
import matplotlib.pyplot as plt

class MPPT_GUI:
    def __init__(self, master):
        self.master = master
        master.title("MPPT 图表查看器")
        self.create_widgets()
        self.current_figures = []  # 存储所有打开的图表窗口
    
    def create_widgets(self):
        frame = ttk.Frame(self.master, padding=20)
        frame.grid(row=0, column=0)
        
        ttk.Button(
            frame,
            text="显示光伏特性曲线",
            command=lambda: self.show_figure(PVPanel.plot_characteristics)
        ).grid(row=0, column=0, pady=5, padx=10)
        
        ttk.Button(
            frame,
            text="显示MPPT仿真结果",
            command=lambda: self.show_figure(self.run_and_plot_simulation)
        ).grid(row=1, column=0, pady=5, padx=10)
        
        ttk.Button(
            frame,
            text="退出程序",
            command=self.cleanup_exit
        ).grid(row=2, column=0, pady=15, padx=10)
    
    def show_figure(self, plot_func):
        """ 统一处理图表显示 """
        plt.close('all')  # 关闭所有旧图表
        plot_func()       # 执行绘图函数
    
    def run_and_plot_simulation(self):
        """ 运行仿真并绘图 """
        v, i, p = run_simulation(step_size=0.1)
        plot_simulation_results(v, i, p)
    
    def cleanup_exit(self):
        """ 清理资源后退出 """
        plt.close('all')
        self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = MPPT_GUI(root)
    root.mainloop()