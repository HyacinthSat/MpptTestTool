import time
import yaml

import numpy as np
from core.algorithms.po_algorithm import PerturbObserveMPPT
from core.pv_simulater import PVPanelSimulator
from analysis.visualizer import SimulationVisualizer

class MPPSimulation:
    def __init__(self, config_file):
        self.config = self._load_config(config_file)
        self.pv = PVPanelSimulator(**self.config['pv_params'])
        self.mppt = PerturbObserveMPPT(**self.config['mppt_params'])
        self.visualizer = SimulationVisualizer()
        
        # 仿真状态变量
        self.history = {
            'time': [],
            'voltage': [],
            'current': [],
            'power': [],
            'duty_cycle': []
        }
        
    def _load_config(self, file_path):
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _simulate_pwm_effect(self, duty_cycle):
        """模拟PWM占空比对系统的影响"""
        # 获取当前IV曲线
        v_range, i_range = self.pv.get_iv_curve()
        
        # 计算工作点（简化模型）
        operating_idx = int(len(v_range) * (1 - duty_cycle))
        return v_range[operating_idx], i_range[operating_idx]
    
    def run(self, duration=60, env_changes=None):
        """运行仿真"""
        start_time = time.time()
        current_time = 0
        
        while current_time < duration:
            # 模拟环境变化
            if env_changes:
                for change in env_changes:
                    if current_time >= change['time']:
                        self.pv.apply_environment_change(**change['params'])
            
            # 获取当前工作点
            v, i = self._simulate_pwm_effect(self.mppt.duty_cycle)
            
            # 更新MPPT算法
            dc = self.mppt.update(v, i)
            
            # 记录数据
            self.history['time'].append(current_time)
            self.history['voltage'].append(v)
            self.history['current'].append(i)
            self.history['power'].append(v*i)
            self.history['duty_cycle'].append(dc)
            
            # 更新显示
            self.visualizer.update(self.history)
            
            # 推进仿真时间
            time.sleep(self.config['sim_step'])
            current_time = time.time() - start_time
        
        self.visualizer.show_final_plot()
        
if __name__ == "__main__":
    # 环境变化配置示例（辐照度突变）
    env_changes = [
        {'time': 20, 'params': {'irradiance': 800}},
        {'time': 40, 'params': {'irradiance': 1200}}
    ]
    
    # 启动仿真
    sim = MPPSimulation('config/sim_config.yaml')
    sim.run(duration=60, env_changes=env_changes)