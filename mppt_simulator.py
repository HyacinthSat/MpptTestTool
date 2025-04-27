# mppt_simulator.py
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
        V = np.clip(V, 0, self.Voc)  # 限制电压输入范围
        I = self.Isc * (self.irrad/1000) * (1 - (V/self.Voc))
        return max(I, 0)
    
    # 在PVPanel类中添加静态方法
    @staticmethod
    def plot_characteristics():
        pv = PVPanel()
        V_range = np.linspace(0, pv.Voc, 100)
        I = [pv.get_output(V) for V in V_range]
        P = [V * i for V, i in zip(V_range, I)]
        
        plt.figure(figsize=(10,4))
        plt.subplot(1,2,1)
        plt.plot(V_range, I, 'b-')
        plt.xlabel('Voltage (V)'), plt.ylabel('Current (A)')
        
        plt.subplot(1,2,2)
        plt.plot(V_range, P, 'r-')
        plt.xlabel('Voltage (V)'), plt.ylabel('Power (W)')
        plt.tight_layout()
        plt.show()

class MPPTController:
    """ P&O MPPT控制器 """
    def __init__(self, step_size=0.5):
        self.step_size = step_size  # 扰动步长
        self.prev_power = 0
        self.voltage = 30  # 初始电压

    def update(self, pv):
        """ 执行一次MPPT算法迭代 """
        current = pv.get_output(self.voltage)
        power = self.voltage * current
         # 限制电压在 [0, Voc]
        
        # 修改后的扰动逻辑
        if power > self.prev_power:
            self.voltage += self.step_size  # 继续同方向
        else:
            self.voltage -= self.step_size  # 仅回退一步（原代码反向扰动幅度过大）
        
        self.voltage = np.clip(self.voltage, 0, pv.Voc) 
        self.prev_power = power
        return self.voltage, current, power

# 仿真运行
if __name__ == "__main__":
    PVPanel.plot_characteristics()
    plt.show(block=False)  # 显示特性曲线

    pv = PVPanel()
    mppt = MPPTController(step_size=0.1)
    
    # 存储仿真数据
    voltages = []
    currents = []
    powers = []
    
    # 运行100次迭代
    for _ in range(100):
        
        V, I, P = mppt.update(pv)
        voltages.append(V)
        currents.append(I)
        powers.append(P)
    
    # 绘制结果
    plt.figure(figsize=(10, 6))
    
    plt.subplot(3, 1, 1)
    plt.plot(voltages, 'b-')
    plt.ylabel('Voltage (V)')
    
    plt.subplot(3, 1, 2)
    plt.plot(currents, 'r-')
    plt.ylabel('Current (A)')
    
    plt.subplot(3, 1, 3)
    plt.plot(powers, 'g-')
    plt.ylabel('Power (W)')
    plt.xlabel('Iterations')
    
    plt.tight_layout()
    plt.show()