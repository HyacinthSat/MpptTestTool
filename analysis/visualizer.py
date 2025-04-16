# analysis/visualizer.py
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec
import numpy as np
from collections import deque

class SimulationVisualizer:
    def __init__(self, max_history=500, refresh_interval=100):
        """
        初始化可视化组件
        
        参数：
            max_history: 最大历史数据点数
            refresh_interval: 动画刷新间隔(毫秒)
        """
        self.max_history = max_history
        self.fig = plt.figure(figsize=(12, 8), facecolor='#f0f0f0')
        self.gs = GridSpec(3, 2, figure=self.fig)
        
        # 初始化子图
        self._init_iv_curve_plot()
        self._init_power_plot()
        self._init_duty_cycle_plot()
        self._init_histogram()
        
        # 数据缓冲区
        self._init_data_buffers()
        
        # 动画配置
        self.ani = animation.FuncAnimation(
            self.fig, 
            self._update, 
            interval=refresh_interval,
            cache_frame_data=False
        )
        
        plt.tight_layout()
    
    def _init_data_buffers(self):
        """初始化数据存储结构"""
        self.time_buffer = deque(maxlen=self.max_history)
        self.voltage_buffer = deque(maxlen=self.max_history)
        self.current_buffer = deque(maxlen=self.max_history)
        self.power_buffer = deque(maxlen=self.max_history)
        self.duty_cycle_buffer = deque(maxlen=self.max_history)
    
    def _init_iv_curve_plot(self):
        """IV特性曲线子图"""
        self.ax_iv = self.fig.add_subplot(self.gs[0, 0])
        self.ax_iv.set_title("实时IV特性曲线", fontsize=10)
        self.ax_iv.set_xlabel("电压 (V)")
        self.ax_iv.set_ylabel("电流 (A)")
        self.iv_line, = self.ax_iv.plot([], [], 'b-', lw=1, label='IV曲线')
        self.operating_point = self.ax_iv.scatter([], [], c='r', s=50, 
                                                label='工作点')
        self.ax_iv.grid(True, alpha=0.3)
        self.ax_iv.legend(loc='upper right')
    
    def _init_power_plot(self):
        """功率跟踪子图"""
        self.ax_power = self.fig.add_subplot(self.gs[1, 0])
        self.ax_power.set_title("功率跟踪过程", fontsize=10)
        self.ax_power.set_ylabel("功率 (W)")
        self.power_line, = self.ax_power.plot([], [], 'g-', lw=1, 
                                            label='实时功率')
        self.max_power_line, = self.ax_power.plot([], [], 'r--', lw=1.5,
                                                label='理论最大功率')
        self.ax_power.grid(True, alpha=0.3)
        self.ax_power.legend(loc='lower right')
    
    def _init_duty_cycle_plot(self):
        """占空比控制子图"""
        self.ax_duty = self.fig.add_subplot(self.gs[2, 0])
        self.ax_duty.set_title("PWM占空比变化", fontsize=10)
        self.ax_duty.set_xlabel("时间 (s)")
        self.ax_duty.set_ylabel("占空比")
        self.duty_line, = self.ax_duty.plot([], [], 'm-', lw=1, 
                                          label='占空比')
        self.ax_duty.grid(True, alpha=0.3)
        self.ax_duty.set_ylim(0, 1)
    
    def _init_histogram(self):
        """效率统计子图"""
        self.ax_hist = self.fig.add_subplot(self.gs[:, 1])
        self.ax_hist.set_title("效率分析", fontsize=10)
        self.ax_hist.set_ylabel("百分比 (%)")
        self.bars = self.ax_hist.bar([], [], color=['#2ca02c', '#d62728'])
        self.ax_hist.set_xticks([])
        self.ax_hist.set_ylim(0, 100)
        self.ax_hist.text(0.5, 0.9, "效率指标", 
                        ha='center', transform=self.ax_hist.transAxes)
    
    def _update(self, frame):
        """动画更新回调函数"""
        # 更新IV曲线
        if hasattr(self, 'iv_curve_data'):
            v, i = self.iv_curve_data
            self.iv_line.set_data(v, i)
            self.ax_iv.relim()
            self.ax_iv.autoscale_view()
        
        # 更新工作点
        if len(self.voltage_buffer) > 0:
            self.operating_point.set_offsets(
                [[self.voltage_buffer[-1], self.current_buffer[-1]]]
            )
        
        # 更新功率曲线
        self.power_line.set_data(self.time_buffer, self.power_buffer)
        if hasattr(self, 'max_power'):
            self.max_power_line.set_data(
                [min(self.time_buffer), max(self.time_buffer)],
                [self.max_power, self.max_power]
            )
        self.ax_power.relim()
        self.ax_power.autoscale_view()
        
        # 更新占空比曲线
        self.duty_line.set_data(self.time_buffer, self.duty_cycle_buffer)
        self.ax_duty.set_xlim(min(self.time_buffer), max(self.time_buffer))
        
        # 更新效率柱状图
        if hasattr(self, 'efficiency'):
            for bar, height in zip(self.bars, self.efficiency.values()):
                bar.set_height(height)
            self.ax_hist.set_ylim(0, max(self.efficiency.values(), default=100)+10)
        
        return (self.iv_line, self.operating_point, self.power_line,
                self.max_power_line, self.duty_line)
    
    def update_iv_curve(self, v, i):
        """更新IV曲线数据"""
        self.iv_curve_data = (v, i)
        self.max_power = np.max(v * i)
    
    def add_data_point(self, time, voltage, current, duty_cycle):
        """
        添加新的数据点
        
        参数：
            time: 时间戳 (s)
            voltage: 当前电压 (V)
            current: 当前电流 (A)
            duty_cycle: PWM占空比 (0-1)
        """
        self.time_buffer.append(time)
        self.voltage_buffer.append(voltage)
        self.current_buffer.append(current)
        self.power_buffer.append(voltage * current)
        self.duty_cycle_buffer.append(duty_cycle)
        
        # 自动计算效率
        if hasattr(self, 'max_power') and self.max_power > 0:
            current_power = voltage * current
            self.efficiency = {
                '跟踪效率': (current_power / self.max_power) * 100,
                '理论极限': 100.0
            }
    
    def show(self):
        """显示可视化窗口"""
        plt.show()
    
    def save_report(self, filename='report.png'):
        """保存分析报告"""
        self.fig.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"报告已保存至 {filename}")

if __name__ == "__main__":
    # 测试可视化组件
    import numpy as np
    from time import time
    
    viz = SimulationVisualizer()
    
    # 生成测试数据
    v = np.linspace(0, 50, 100)
    i = 10 * (1 - (v/50)**2)
    viz.update_iv_curve(v, i)
    
    # 模拟数据更新
    start_time = time()
    for dc in np.linspace(0, 1, 200):
        t = time() - start_time
        idx = int(dc * len(v))
        viz.add_data_point(t, v[idx], i[idx], dc)
        plt.pause(0.01)
    
    viz.show()