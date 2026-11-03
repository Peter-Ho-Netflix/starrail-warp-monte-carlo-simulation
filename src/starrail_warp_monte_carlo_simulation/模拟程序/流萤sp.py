# 计算抽虚照和不抽虚照对抽流萤sp的6+5的概率扰动
from dataclasses import dataclass
from starrail_warp_monte_carlo_simulation.logic import run
from tqdm.contrib.concurrent import process_map
from pathlib import Path
import tomllib
import csv
import matplotlib.pyplot as plt
from datetime import datetime

def run_with_nihilux(
    s5_char_pity_count: int, 
    s5_light_cone_pity_count: int,
    s4_char_pity_count: int,
    s4_light_cone_pity_count: int,
    s4_char_owner_count_list: list[int],
    s5_char_owner_count_list: list[int]):
    '''
    计算抽虚照的情况下抽流萤sp所需的概率分布曲线和抽数
    '''
    current_s4_char_owner_count_list = s4_char_owner_count_list
    current_s5_char_owner_count_list = s5_char_owner_count_list
    # 抽虚照
    nihilux_simulation_result = run(1, 1, s5_char_pity_count=s5_char_pity_count, s5_light_cone_pity_count=s5_light_cone_pity_count, s4_char_pity_count=s4_char_pity_count, s4_light_cone_pity_count=s4_light_cone_pity_count, s4_char_eidolon_list=current_s4_char_owner_count_list, s5_char_eidolon_list=current_s5_char_owner_count_list)
    # 预处理抽流萤sp的命座图谱
    current_s4_char_owner_count_list = sorted(nihilux_simulation_result.s4_char_eidolon_list)
    current_s5_char_owner_count_list = nihilux_simulation_result.s5_char_eidolon_list
    current_s5_char_owner_count_list[0] = 0 # 本期UP角色不计入命座图谱
    # 抽流萤sp
    firefly_sp_simulation_result = run(7, 5, s4_char_eidolon_list=current_s4_char_owner_count_list, s5_char_eidolon_list=current_s5_char_owner_count_list)
    return nihilux_simulation_result.total_warp_count+firefly_sp_simulation_result.total_warp_count, nihilux_simulation_result.total_resources_count+firefly_sp_simulation_result.total_resources_count

@dataclass
class RunPairResult:
    '''
    抽虚照和不抽虚照对抽流萤sp的6+5的概率扰动结果
    '''
    firefly_only_warp_count: int
    firefly_only_resources_count: int
    firefly_with_nihilux_warp_count: int
    firefly_with_nihilux_resources_count: int

def run_pair(
    s5_char_pity_count: int, 
    s5_light_cone_pity_count: int,
    s4_char_pity_count: int,
    s4_light_cone_pity_count: int,
    s4_char_owner_count_list: list[int],
    s5_char_owner_count_list: list[int]):
    '''
    计算抽虚照和不抽虚照对抽流萤sp的6+5的概率扰动
    '''
    # 模拟只抽流萤sp
    current_s4_char_owner_count_list = sorted(s4_char_owner_count_list)
    current_s5_char_owner_count_list = s5_char_owner_count_list
    firefly_only_simulation_result = run(7, 5, s4_char_eidolon_list=current_s4_char_owner_count_list, s5_char_eidolon_list=current_s5_char_owner_count_list)
    # 模拟抽虚照的情况下抽流萤sp
    firefly_simulation_result_with_nihilux = run_with_nihilux(s5_char_pity_count, s5_light_cone_pity_count, s4_char_pity_count, s4_light_cone_pity_count, s4_char_owner_count_list, s5_char_owner_count_list)
    return RunPairResult(
        firefly_only_warp_count=firefly_only_simulation_result.total_warp_count,
        firefly_only_resources_count=firefly_only_simulation_result.total_resources_count,
        firefly_with_nihilux_warp_count=firefly_simulation_result_with_nihilux[0],
        firefly_with_nihilux_resources_count=firefly_simulation_result_with_nihilux[1],
    )

def main():
    print("================================================")
    print("欢迎使用崩坏星穹铁道抽卡蒙特卡洛模拟-流萤sp抽卡计算子程序")
    print("================================================")
    config_path = Path(__file__).parent.with_name("config.toml")
    with config_path.open("rb") as f:
        config = tomllib.load(f)
    simulation_result = process_map(run_pair, 
        [config["firefly_sp_config"]["s5_char_pity_count"]] * config["common"]["simulation_samples"], 
        [config["firefly_sp_config"]["s5_light_cone_pity_count"]] * config["common"]["simulation_samples"], 
        [config["firefly_sp_config"]["s4_char_pity_count"]] * config["common"]["simulation_samples"], 
        [config["firefly_sp_config"]["s4_light_cone_pity_count"]] * config["common"]["simulation_samples"], 
        [config["firefly_sp_config"]["s4_char_owner_count_list"]] * config["common"]["simulation_samples"], 
        [config["firefly_sp_config"]["s5_char_owner_count_list"]] * config["common"]["simulation_samples"], 
        max_workers=config["common"]["max_threads"], 
        chunksize=config["common"]["chunk_size"])
    firefly_only_warp_counts = [result.firefly_only_warp_count for result in simulation_result]
    firefly_only_resources_counts = [result.firefly_only_resources_count for result in simulation_result]
    firefly_with_nihilux_warp_counts = [result.firefly_with_nihilux_warp_count for result in simulation_result]
    firefly_with_nihilux_resources_counts = [result.firefly_with_nihilux_resources_count for result in simulation_result]
    with open(f"输出文件/流萤sp-{datetime.now().strftime('%Y%m%d%H%M%S')}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["模拟次数", "抽流萤sp所需抽卡次数", "抽流萤sp所需资源数量", "抽流萤sp+抽虚照所需抽卡次数", "抽流萤sp+抽虚照所需资源数量"])
        writer.writerows(zip(range(len(firefly_only_warp_counts)), firefly_only_warp_counts, firefly_only_resources_counts, firefly_with_nihilux_warp_counts, firefly_with_nihilux_resources_counts))
    print("流萤sp模拟完成")
    plt.figure()
    plt.rcParams["font.sans-serif"] = ["Microsoft Yahei UI"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.hist(firefly_only_warp_counts, bins=range(min(firefly_only_warp_counts), max(firefly_only_warp_counts) + 1))
    plt.xlabel("抽卡次数")
    plt.ylabel("频数")
    plt.title("抽流萤sp所需抽卡次数频数分布直方图")
    plt.figure()
    plt.rcParams["font.sans-serif"] = ["Microsoft Yahei UI"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.hist(firefly_with_nihilux_warp_counts, bins=range(min(firefly_with_nihilux_warp_counts), max(firefly_with_nihilux_warp_counts) + 1))
    plt.xlabel("抽卡次数")
    plt.ylabel("频数")
    plt.title("抽流萤sp+抽虚照所需抽卡次数频数分布直方图")
    plt.figure()
    plt.rcParams["font.sans-serif"] = ["Microsoft Yahei UI"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.ecdf(firefly_only_resources_counts, color='violet', label='只抽流萤sp')
    plt.ecdf(firefly_with_nihilux_resources_counts, color='blue', label='抽流萤sp+抽虚照')
    plt.xlabel("所需资源数量")
    plt.ylabel("概率")
    plt.title("所需资源数量概率分布曲线（按专票计算）")
    plt.legend()
    plt.show()