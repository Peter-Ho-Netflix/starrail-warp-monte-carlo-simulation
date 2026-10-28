from statistics import mean, mode, median
from starrail_warp_monte_carlo_simulation.logic import SimulationProcess
from tqdm.contrib.concurrent import process_map
import matplotlib.pyplot as plt
import tomllib

def run_simulation(char_count: int, light_cone_count: int) -> int:
    simulation_process = SimulationProcess()
    return simulation_process.run(char_count, light_cone_count)

def main():
    print("================================================")
    print("欢迎使用崩坏星穹铁道抽卡蒙特卡洛模拟")
    print("================================================")
    with open("src/starrail_warp_monte_carlo_simulation/config.toml", "rb") as f:
        config = tomllib.load(f)
    char_count_input = input("请输入目标角色数量，为空代表不抽角色：")
    light_cone_count_input = input("请输入目标光锥数量，为空代表不抽光锥：")
    char_count = 0
    light_cone_count = 0
    if char_count_input:
        char_count = int(char_count_input)
    if light_cone_count_input:
        light_cone_count = int(light_cone_count_input)
    simulation_samples = config["common"]["simulation_samples"]
    max_threads = config["common"]["max_threads"]
    chunk_size = config["common"]["chunk_size"]
    # 先执行一次run函数进行测试
    # simulation_process = SimulationProcess()
    # total_warp_count = simulation_process.run(char_count, light_cone_count)
    # print(f"抽到目标角色和光锥所需的总抽卡次数：{total_warp_count}")

    warp_counts = process_map(run_simulation, [char_count] * simulation_samples, [light_cone_count] * simulation_samples, max_workers=max_threads, chunksize=chunk_size)
    plt.figure()
    plt.hist(warp_counts, bins=range(min(warp_counts), max(warp_counts) + 1))
    plt.figure()
    print(f"最坏情况抽卡次数：{max(warp_counts)}")
    print(f"抽卡次数众数：{mode(warp_counts)}")
    print(f"抽卡次数平均值：{mean(warp_counts)}")
    print(f"抽卡次数中位数：{median(warp_counts)}")
    plt.hist(warp_counts, bins=range(min(warp_counts), max(warp_counts) + 1), density=True, cumulative=True, edgecolor='violet')
    plt.show()

if __name__ == "__main__":
    main()