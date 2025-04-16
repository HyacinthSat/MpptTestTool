class PerturbObserveMPPT:
    def __init__(self, step_size=0.01, max_duty=0.95, min_duty=0.05):
        self.step = step_size
        self.max_dc = max_duty
        self.min_dc = min_duty
        self.prev_power = 0
        self.duty_cycle = 0.5  # 初始占空比
        
    def update(self, voltage, current):
        """执行算法迭代"""
        current_power = voltage * current
        
        # 确定扰动方向
        if current_power > self.prev_power:
            direction = 1 if (voltage > self.prev_voltage) else -1
        else:
            direction = -1 if (voltage > self.prev_voltage) else 1
            
        # 更新占空比
        new_dc = self.duty_cycle + direction * self.step
        self.duty_cycle = max(self.min_dc, min(self.max_dc, new_dc))
        
        # 保存状态
        self.prev_power = current_power
        self.prev_voltage = voltage
        return self.duty_cycle