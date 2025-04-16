import numpy as np

class PVPanelSimulator:
    """光伏面板特性模拟器"""
    def __init__(self, 
                 v_oc=48.0, 
                 i_sc=10.0, 
                 cell_temp=25, 
                 irradiance=1000):
        self.v_oc = v_oc  # 开路电压(V)
        self.i_sc = i_sc  # 短路电流(A)
        self.temp = cell_temp  # 电池温度(℃)
        self.irradiance = irradiance  # 辐照度(W/m²)
        
        # 电气特性参数
        self.r_sh = 100.0   # 并联电阻(Ω)
        self.r_s = 0.5      # 串联电阻(Ω)
        self.a = 1.3        # 二极管特性因子
        
    def get_iv_curve(self, points=100):
        """生成IV特性曲线"""
        v = np.linspace(0, self.v_oc, points)
        i = self._calculate_current(v)
        return v, np.maximum(i, 0)
    
    def _calculate_current(self, v):
        """基于单二极管模型的计算"""
        k = 1.380649e-23
        q = 1.602e-19
        T = 273.15 + self.temp
        
        # 光生电流
        I_ph = (self.irradiance / 1000) * self.i_sc * (1 + 0.0025*(self.temp-25))
        
        # 二极管饱和电流
        I_0 = 1e-9 * (T/300)**3
        
        # 输出电流计算
        term1 = (v + self.r_s * I_ph) / (self.r_sh)
        term2 = I_0 * (np.exp(q*(v + I_ph*self.r_s)/(self.a*k*T)) - 1)
        return I_ph - term1 - term2
        
    def apply_environment_change(self, irradiance=None, temp=None):
        """模拟环境变化"""
        if irradiance:
            self.irradiance = max(100, min(1500, irradiance))
        if temp:
            self.temp = max(-10, min(80, temp))