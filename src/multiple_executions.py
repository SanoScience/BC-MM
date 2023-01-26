import os
import config
from simulation import Simulation

SIMULATION_NUMBER = 100


def start_simulation():
    simulation = Simulation()
    simulation.start()


def multiple_executions():
    with open(os.path.join(config.PATH_OUTPUT, config.COSTS_SUMMARY_ALL_FILE_NAME), "a") as f:
        to_write = "SIM_ID,DIRECT,TOTAL,INDIRECT_OTHERS,INDIRECT_DEATH\n"
        f.write(to_write)
    for i in range(SIMULATION_NUMBER):
        config.SEED = i
        start_simulation()


if __name__ == "__main__":
    multiple_executions()
