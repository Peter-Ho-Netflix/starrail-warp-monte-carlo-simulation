from statistics import mean, mode, median
from starrail_warp_monte_carlo_simulation.logic import run
from tqdm.contrib.concurrent import process_map
import matplotlib.pyplot as plt
import tomllib
from pathlib import Path

def main():
    print("================================================")
    print("欢迎使用崩坏星穹铁道抽卡蒙特卡洛模拟")
    print("================================================")
    config_path = Path(__file__).with_name("config.toml")
    with config_path.open("rb") as f:
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
    # # 先执行一次run函数进行测试
    # total_warp_count = run(char_count, light_cone_count)
    # print(f"抽到目标角色和光锥所需的总抽卡次数和所需资源数量：{total_warp_count}")

    data_list = process_map(run, [char_count] * simulation_samples, [light_cone_count] * simulation_samples, max_workers=max_threads, chunksize=chunk_size)
    warp_counts = [data[0] for data in data_list]
    resources_counts = [data[1] for data in data_list]
    plt.figure()
    plt.rcParams["font.sans-serif"] = ["Microsoft Yahei UI"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.hist(warp_counts, bins=range(min(warp_counts), max(warp_counts) + 1))
    plt.xlabel("抽卡次数")
    plt.ylabel("频数")
    plt.title("抽卡次数频数分布直方图")
    print(f"最坏情况抽卡次数：{max(warp_counts)}")
    print(f"抽卡次数众数：{mode(warp_counts)}")
    print(f"抽卡次数平均值：{mean(warp_counts)}")
    print(f"抽卡次数中位数：{median(warp_counts)}")
    plt.figure()
    plt.rcParams["font.sans-serif"] = ["Microsoft Yahei UI"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.hist(resources_counts, bins=range(min(resources_counts), max(resources_counts) + 1), density=True, cumulative=True, edgecolor='violet')
    plt.xlabel("所需资源数量")
    plt.ylabel("概率")
    plt.title("所需资源数量概率分布曲线（按专票计算）")
    print(f"最坏情况所需资源数量：{max(resources_counts)}")
    print(f"所需资源数量众数：{mode(resources_counts)}")
    print(f"所需资源数量平均值：{mean(resources_counts)}")
    print(f"所需资源数量中位数：{median(resources_counts)}")
    plt.show()

if __name__ == "__main__":
    main()