from enum import Enum
import random
import tomllib
from pathlib import Path

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

def normalize_list(list: list[int] | None, count: int) -> list[int]:
    result = [0] * count
    if list:
        n = min(count, len(list))
        result[:n] = list[:n]
    return result

def run(
    s5_char_tgt_count: int, 
    s5_light_cone_tgt_count: int, 
    s5_char_pity_count: int = 0, 
    s5_light_cone_pity_count: int = 0, 
    s4_char_pity_count: int = 0, 
    s4_light_cone_pity_count: int = 0, 
    s5_char_astray: bool = False,
    s5_light_cone_astray: bool = False,
    s4_char_astray: bool = False,
    s4_light_cone_astray: bool = False,
    s4_char_eidolon_list: list[int] | None = None, 
    s5_char_eidolon_list: list[int] | None = None) -> tuple[int, int]:
    '''
    顺序执行所有抽卡，直到抽到目标角色数量和目标光锥数量
    
    角色数量 = 星魂 + 1。满命为 7，尚未拥有为 0。
    
    已拥有数量列表如果不满整个列表（如5星角色列表不满8个元素，其中常驻7个，UP 1个），则缺损项默认视为没有

    如果给出的列表数量超出实际数量，则会切片至目标数量，如5星角色列表实际给了10个，则只取前8个元素带入进行计算，超出部分会被舍弃。

    不计光锥列表，因为已拥有光锥对于抽卡所需资源计算结果不构成扰动

    Args:
        s5_char_tgt_count (int): 目标5星角色数量
        s5_light_cone_tgt_count (int): 目标5星光锥数量
        s5_char_pity_count (int): 5星角色已垫抽次数
        s5_light_cone_pity_count (int): 5星光锥已垫抽次数
        s4_char_pity_count (int): 4星角色已垫抽次数
        s4_light_cone_pity_count (int): 4星光锥已垫抽次数
        s5_char_astray (bool): 5星角色是否已歪
        s5_light_cone_astray (bool): 5星光锥是否已歪
        s4_char_astray (bool): 4星角色是否已歪
        s4_light_cone_astray (bool): 4星光锥是否已歪
        s4_char_eidolon_list (list[int]): 四星角色已拥有数量。前三项是本期 UP 角色，这三项适用四星大保底。
        s5_char_eidolon_list (list[int]): 五星角色已拥有数量。第一项是本期 UP 角色，这项适用五星大保底。

    Returns:
        tuple[int, int]: 所需抽卡次数和所需资源次数
    '''
    simulation_logic = SimulationLogic(
        initial_char_s5_warp_count=s5_char_pity_count,
        initial_char_s4_warp_count=s4_char_pity_count,
        initial_light_cone_s5_warp_count=s5_light_cone_pity_count,
        initial_light_cone_s4_warp_count=s4_light_cone_pity_count,
        initial_char_s5_astray=s5_char_astray,
        initial_char_s4_astray=s4_char_astray,
        initial_light_cone_s5_astray=s5_light_cone_astray,
        initial_light_cone_s4_astray=s4_light_cone_astray,
    )
    current_s5_tgt_char_count = 0
    current_s5_bypass_char_count = 0
    current_s4_char_count = 0
    current_s5_tgt_light_cone_count = 0
    current_s5_bypass_light_cone_count = 0
    current_s4_light_cone_count = 0
    total_warp_count = 0
    undying_starlight_count = 0  # 每20星芒可以兑换1抽，用于资源计数
    total_resources_count = 0

    config_path = Path(__file__).with_name("config.toml")
    with config_path.open("rb") as f:
        config = tomllib.load(f)
    s4_char_count = config["warp_config"]["s4_char_count"]
    s4_light_cone_count = config["warp_config"]["s4_light_cone_count"]
    s4_total_count = s4_char_count + s4_light_cone_count

    # 补齐4星角色列表到22个元素
    s4_char_eidolon_list = normalize_list(s4_char_eidolon_list, s4_char_count)
    # 补齐5星角色列表到8个元素
    s5_char_eidolon_list = normalize_list(s5_char_eidolon_list, 8)

    while current_s5_tgt_char_count < s5_char_tgt_count:
        total_warp_count += 1
        result = simulation_logic.char_warp()
        if result == WarpResult.S5_TGT:
            current_s5_tgt_char_count += 1
            # print(f"第{total_warp_count}抽抽到限定5星角色")
            if s5_char_eidolon_list[0] >= 7:
                undying_starlight_count += 100
            else:
                undying_starlight_count += 40
                s5_char_eidolon_list[0] += 1
            # print(f"当前5星角色已拥有数量：{s5_char_eidolon_list}")
            # print(f"当前已获得星芒数量：{undying_starlight_count}")
        elif result == WarpResult.S5_BYPASS:
            current_s5_bypass_char_count += 1
            # print(f"第{total_warp_count}抽抽到非限定5星角色")
            char_index = random.randint(1, 7)
            if s5_char_eidolon_list[char_index] >= 7:
                undying_starlight_count += 100
            else:
                undying_starlight_count += 40
                s5_char_eidolon_list[char_index] += 1
            # print(f"当前5星角色已拥有数量：{s5_char_eidolon_list}")
            # print(f"当前已获得星芒数量：{undying_starlight_count}")
        elif result == WarpResult.S4_TGT or result == WarpResult.S4_BYPASS:
            current_s4_char_count += 1
            # print(f"第{total_warp_count}抽抽到4星角色")
            if result == WarpResult.S4_TGT:
                # 此时从前三个角色中选择一个角色进行抽取
                char_index = random.randint(0, 2)
                # print(f"当前随机值：{char_index}")
                if s4_char_eidolon_list[char_index] >= 7:
                    undying_starlight_count += 20
                    # print("抽到限定已满命四星角色")
                else:
                    undying_starlight_count += 8
                    s4_char_eidolon_list[char_index] += 1
                    # print(f"抽到限定未满命四星角色，当前已拥有数量：{s4_char_eidolon_list[char_index]}")
            elif result == WarpResult.S4_BYPASS:
                # 此时从后面角色或光锥中选一个获得
                char_index = random.randint(3, s4_total_count - 1)
                # print(f"当前随机值：{char_index}")
                if char_index < s4_char_count:
                    # 此时抽到的是角色
                    if s4_char_eidolon_list[char_index] >= 7:
                        undying_starlight_count += 20
                        # print("抽到非限定已满命四星角色")
                    else:
                        undying_starlight_count += 8
                        s4_char_eidolon_list[char_index] += 1
                        # print(f"抽到非限定未满命四星角色，当前已拥有数量：{s4_char_eidolon_list[char_index]}")
                else:
                    # 此时抽到的是光锥
                    undying_starlight_count += 8
                    # print("抽到四星光锥")
            # print(f"当前4星角色已拥有数量：{s4_char_eidolon_list}")
            # print(f"当前已获得星芒数量：{undying_starlight_count}")
    while current_s5_tgt_light_cone_count < s5_light_cone_tgt_count:
        total_warp_count += 1
        result = simulation_logic.light_cone_warp()
        if result == WarpResult.S5_TGT:
            current_s5_tgt_light_cone_count += 1
            # print(f"第{total_warp_count}抽抽到限定5星光锥")
            undying_starlight_count += 40
            # print(f"当前已获得星芒数量：{undying_starlight_count}")
        elif result == WarpResult.S5_BYPASS:
            current_s5_bypass_light_cone_count += 1
            # print(f"第{total_warp_count}抽抽到非限定5星光锥")
            undying_starlight_count += 40
            # print(f"当前已获得星芒数量：{undying_starlight_count}")
        elif result == WarpResult.S4_TGT or result == WarpResult.S4_BYPASS:
            current_s4_light_cone_count += 1
            # print(f"第{total_warp_count}抽抽到4星光锥")
            undying_starlight_count += 8
            # print(f"当前已获得星芒数量：{undying_starlight_count}")
    total_resources_count = total_warp_count - undying_starlight_count // 20
    return total_warp_count, total_resources_count