from enum import Enum
import random

class WarpResult(Enum):
    S5_TGT = 0,
    S5_BYPASS = 1,
    S4_TGT = 2,
    S4_BYPASS = 3,
    S3 = 4,

class SimulationLogic:
    def __init__(self, 
    initial_char_s5_warp_count: int = 0, initial_char_s4_warp_count: int = 0, 
    initial_light_cone_s5_warp_count: int = 0, initial_light_cone_s4_warp_count: int = 0,
    initial_char_s5_astray: bool = False, initial_char_s4_astray: bool = False,
    initial_light_cone_s5_astray: bool = False, initial_light_cone_s4_astray: bool = False):
        self.char_s5_warp_count = initial_char_s5_warp_count
        self.char_s4_warp_count = initial_char_s4_warp_count
        self.light_cone_s5_warp_count = initial_light_cone_s5_warp_count
        self.light_cone_s4_warp_count = initial_light_cone_s4_warp_count
        self.char_s5_astray = initial_char_s5_astray
        self.char_s4_astray = initial_char_s4_astray
        self.light_cone_s5_astray = initial_light_cone_s5_astray
        self.light_cone_s4_astray = initial_light_cone_s4_astray
    
    def char_warp(self) -> WarpResult:
        self.char_s5_warp_count += 1
        self.char_s4_warp_count += 1
        s5_random_probability = 6e-3
        if self.char_s5_warp_count > 73:
            s5_random_probability = 6e-3+(1-6e-3)*abs(self.char_s5_warp_count-73)/(90-73)
        s4_random_probability = 5.1e-2
        if self.char_s4_warp_count > 8:
            s4_random_probability = 5.1e-2+(1-5.1e-2)*abs(self.char_s4_warp_count-8)/2
        if random.random() < s5_random_probability:
            # 此时角色有50%的概率歪，50%的概率不歪，如果此前抽到过歪，则本次一定不会歪
            if self.char_s5_astray or random.random() < 0.5:
                self.char_s5_astray = False
                self.char_s5_warp_count = 0
                return WarpResult.S5_TGT
            else:
                self.char_s5_astray = True
                self.char_s5_warp_count = 0
                return WarpResult.S5_BYPASS
        elif random.random() < s4_random_probability:
            if self.char_s4_astray or random.random() < 0.5:
                self.char_s4_astray = False
                self.char_s4_warp_count = 0
                return WarpResult.S4_TGT
            else:
                self.char_s4_astray = True
                self.char_s4_warp_count = 0
                return WarpResult.S4_BYPASS
        else:
            return WarpResult.S3
    
    def light_cone_warp(self) -> WarpResult:
        self.light_cone_s5_warp_count += 1
        s5_random_probability = 8e-3
        if self.light_cone_s5_warp_count > 59:
            s5_random_probability = 8e-3+(1-8e-3)*abs(self.light_cone_s5_warp_count-65)/(80-65)
        s4_random_probability = 6.6e-2
        if self.light_cone_s4_warp_count > 8:
            s4_random_probability = 6.6e-2+(1-6.6e-2)*abs(self.light_cone_s4_warp_count-7)/2
        if random.random() < s5_random_probability:
            # 此时光锥有25%的概率歪，75%的概率不歪，如果此前抽到过歪，则本次一定不会歪
            if self.light_cone_s5_astray or random.random() < 0.75:
                self.light_cone_s5_astray = False
                self.light_cone_s5_warp_count = 0
                return WarpResult.S5_TGT
            else:
                self.light_cone_s5_astray = True
                self.light_cone_s5_warp_count = 0
                return WarpResult.S5_BYPASS
        elif random.random() < s4_random_probability:
            if self.light_cone_s4_astray or random.random() < 0.75:
                self.light_cone_s4_astray = False
                self.light_cone_s4_warp_count = 0
                return WarpResult.S4_TGT
            else:
                self.light_cone_s4_astray = True
                self.light_cone_s4_warp_count = 0
                return WarpResult.S4_BYPASS
        else:
            return WarpResult.S3

    
def run(simulation_logic: SimulationLogic, s5_char_tgt_count: int, s5_light_cone_tgt_count: int) -> tuple[int, int]:
    '''
    顺序执行所有抽卡，直到抽到目标角色数量

    Args:
        simulation_logic: 模拟逻辑类
        s5_char_tgt_count: 目标5星角色数量
        s5_light_cone_tgt_count: 目标5星光锥数量

    Returns:
        total_warp_count: 所需抽卡次数
        total_resources_count: 所需资源次数
    '''
    current_s5_tgt_char_count = 0
    current_s5_bypass_char_count = 0
    current_s4_char_count = 0
    current_s5_tgt_light_cone_count = 0
    current_s5_bypass_light_cone_count = 0
    current_s4_light_cone_count = 0
    total_warp_count = 0
    undying_starlight_count = 0  # 每20星芒可以兑换1抽，用于资源计数
    total_resources_count = 0
    while current_s5_tgt_char_count < s5_char_tgt_count:
        total_warp_count += 1
        result = simulation_logic.char_warp()
        if result == WarpResult.S5_TGT:
            current_s5_tgt_char_count += 1
            # print(f"第{total_warp_count}抽抽到限定5星角色")
            undying_starlight_count += 40
        elif result == WarpResult.S5_BYPASS:
            current_s5_bypass_char_count += 1
            # print(f"第{total_warp_count}抽抽到非限定5星角色")
            undying_starlight_count += 40
        elif result == WarpResult.S4_TGT or result == WarpResult.S4_BYPASS:
            current_s4_char_count += 1
            # print(f"第{total_warp_count}抽抽到4星角色")
            undying_starlight_count += 8
    while current_s5_tgt_light_cone_count < s5_light_cone_tgt_count:
        total_warp_count += 1
        result = simulation_logic.light_cone_warp()
        if result == WarpResult.S5_TGT:
            current_s5_tgt_light_cone_count += 1
            # print(f"第{total_warp_count}抽抽到限定5星光锥")
            undying_starlight_count += 40
        elif result == WarpResult.S5_BYPASS:
            current_s5_bypass_light_cone_count += 1
            # print(f"第{total_warp_count}抽抽到非限定5星光锥")
            undying_starlight_count += 40
        elif result == WarpResult.S4_TGT or result == WarpResult.S4_BYPASS:
            current_s4_light_cone_count += 1
            # print(f"第{total_warp_count}抽抽到4星光锥")
            undying_starlight_count += 8
    total_resources_count = total_warp_count - undying_starlight_count // 20
    return total_warp_count, total_resources_count