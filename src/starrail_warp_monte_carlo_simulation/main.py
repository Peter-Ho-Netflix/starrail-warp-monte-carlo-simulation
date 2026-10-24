from starrail_warp_monte_carlo_simulation.logic import SimulationLogic
from tqdm.contrib.concurrent import process_map
import tomllib

def main():
    print("================================================")
    print("欢迎使用崩坏星穹铁道抽卡蒙特卡洛模拟")
    print("================================================")
    simulation_logic = SimulationLogic()
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

if __name__ == "__main__":
    main()