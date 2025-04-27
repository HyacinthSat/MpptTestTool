import numpy as np
import matplotlib.pyplot as plt

class PVPanel:
    """ 光伏电池模型 """
    def __init__(self):
        self.Voc = 40      # 开路电压 (V)
        self.Isc = 8.5     # 短路电流 (A)
        self.Vmpp = 32     # 最大功率点电压
        self.Impp = 7.8    # 最大功率点电流
        self.temp = 25     # 温度 (°C)
        self.irrad = 1000  # 辐照度 (W/m²)

    def get_output(self, V):
        V = np.clip(V, 0, self.Voc)
        I = self.Isc * (self.irrad/1000) * (1 - (V/self.Voc))
        return max(I, 0)
    
    @staticmethod
    def plot_characteristics():
        pv = PVPanel()
        V_range = np.linspace(0, pv.Voc, 100)
        I = [pv.get_output(V) for V in V_range]
        P = [V * i for V, i in zip(V_range, I)]
        
        plt.figure("PV Characteristics", figsize=(10,4))
        plt.subplot(1,2,1)
        plt.plot(V_range, I, 'b-')
        plt.xlabel('Voltage (V)'), plt.ylabel('Current (A)')
        plt.grid(True)
        
        plt.subplot(1,2,2)
        plt.plot(V_range, P, 'r-')
        plt.xlabel('Voltage (V)'), plt.ylabel('Power (W)')
        plt.grid(True)
        plt.tight_layout()
        plt.show(block=False)  # 非阻塞显示

class MPPTController:
    """ P&O MPPT控制器 """
    def __init__(self, step_size=0.5):
        self.step_size = step_size
        self.prev_power = 0
        self.voltage = 30  # 初始电压

    def update(self, pv):
        current = pv.get_output(self.voltage)
        power = self.voltage * current
        
        if power > self.prev_power:
            self.voltage += self.step_size
        else:
            self.voltage -= self.step_size
        
        self.voltage = np.clip(self.voltage, 0, pv.Voc)
        self.prev_power = power
        return self.voltage, current, power

# ---------- 模块级函数 ----------
def run_simulation(step_size=0.1, iterations=100):
    """ 运行仿真并返回数据 """
    pv = PVPanel()
    mppt = MPPTController(step_size=step_size)
    
    voltages, currents, powers = [], [], []
    for _ in range(iterations):
        V, I, P = mppt.update(pv)
        voltages.append(V)
        currents.append(I)
        powers.append(P)
    
    return voltages, currents, powers

def plot_simulation_results(voltages, currents, powers):
    """ 绘制仿真结果 """
    plt.figure("MPPT Simulation Results", figsize=(10,6))
    plt.subplot(3,1,1)
    plt.plot(voltages, 'b-'), plt.ylabel('Voltage (V)'), plt.grid(True)
    plt.subplot(3,1,2)
    plt.plot(currents, 'r-'), plt.ylabel('Current (A)'), plt.grid(True)
    plt.subplot(3,1,3)
    plt.plot(powers, 'g-'), plt.ylabel('Power (W)'), plt.xlabel('Iterations'), plt.grid(True)
    plt.tight_layout()
    plt.show(block=False)

# ---------- 主程序 ----------
if __name__ == "__main__":
    PVPanel.plot_characteristics()       # 显示光伏特性曲线
    v, i, p = run_simulation(step_size=0.1)
    plot_simulation_results(v, i, p)     # 显示仿真结果
    plt.show()                           # 统一激活窗口