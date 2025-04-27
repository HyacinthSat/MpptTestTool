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
        """ 根据输出电压计算电流（简化模型）"""
        # 简化模型公式：I = Isc - (Isc/Voc) * V
        I = self.Isc * (self.irrad/1000) - (self.Isc/self.Voc) * V
        return max(I, 0)  # 电流不能为负

class MPPTController:
    """ P&O MPPT控制器 """
    def __init__(self, step_size=0.5):
        self.step_size = step_size  # 扰动步长
        self.prev_power = 0
        self.voltage = 0  # 初始电压

    def update(self, pv):
        """ 执行一次MPPT算法迭代 """
        current = pv.get_output(self.voltage)
        power = self.voltage * current
        self.voltage = np.clip(self.voltage, 0, pv.Voc)  # 限制电压在 [0, Voc]
        
        # 修改后的扰动逻辑
        if power > self.prev_power:
            self.voltage += self.step_size  # 继续同方向
        else:
            self.voltage -= self.step_size  # 仅回退一步（原代码反向扰动幅度过大）
        
        self.prev_power = power
        return self.voltage, current, power

# 仿真运行
if __name__ == "__main__":
    pv = PVPanel()
    mppt = MPPTController()
    
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