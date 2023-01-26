from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from collections import Counter
from config import PLOT_HISTORY, PATH_OUTPUT, COSTS_FILENAME, STATES_FILENAME, NO_ITERATIONS, HEALTHY_ON_INIT, EDGES, \
    STATE_TRANSITIONS_FILENAME, COSTS_SUMMARY_FILE_NAME, COSTS_SUMMARY_ALL_FILE_NAME
from costs import Cost

import os

from plotting import DynamicPlot

if TYPE_CHECKING:
    from states import State, TransitionOutput
    from model import Model
    from person import Person


class History(ABC):
    def __init__(self):
        pass


class PersonHistory(History):
    def __init__(self, state: 'State', time_in_state: int, age: int):
        super(PersonHistory, self).__init__()
        self.init_time_in_state = time_in_state
        self.state_history = [state.name]
        self.age_history = [age]
        self.times_in_state_history = []

    def update(self, transition_output: 'TransitionOutput', iteration):
        if transition_output.moved_to_new_state:
            if len(self.state_history) == 1:
                self.times_in_state_history.append(self.init_time_in_state + iteration - 1)
            else:
                self.times_in_state_history.append(iteration - sum(self.times_in_state_history))

            self.state_history.append(transition_output.state.name)
        return self, transition_output


class GlobalHistory(History):
    def __init__(self, model: 'Model', sim_id: str):
        super(GlobalHistory, self).__init__()
        self.model = model
        self.state_counters = []
        self.costs_counters = []
        self.state_transition_counters = []
        self.current_iteration = 0
        self.person_histories = {}
        self.sim_id = sim_id

        os.makedirs(os.path.join(PATH_OUTPUT, sim_id), exist_ok=True)
        self.states_file_path = os.path.join(PATH_OUTPUT, sim_id, f"{self.sim_id}_{STATES_FILENAME}")
        self.costs_file_path = os.path.join(PATH_OUTPUT, sim_id, f"{self.sim_id}_{COSTS_FILENAME}")
        self.costs_summary_file_path = os.path.join(PATH_OUTPUT, sim_id, f"{self.sim_id}_{COSTS_SUMMARY_FILE_NAME}")
        self.costs_summary_all_file_path = os.path.join(PATH_OUTPUT, f"{COSTS_SUMMARY_ALL_FILE_NAME}")
        self.state_transitions_file_path = os.path.join(PATH_OUTPUT, sim_id,
                                                        f"{self.sim_id}_{STATE_TRANSITIONS_FILENAME}")

        self.all_dead = 0

        if PLOT_HISTORY:
            self.dynamic_plot = DynamicPlot(self.sim_id)

    def add_person_history(self, person: 'Person'):
        self.person_histories[person.uuid] = person.history
        self.update_init_iteration(person)

    def update(self, person_history_output):
        person_history, transition_output = person_history_output[0], person_history_output[1]
        self.state_counters[self.current_iteration][transition_output.state.name] += 1
        self.costs_counters[self.current_iteration] += transition_output.cost
        self.state_transition_counters[self.current_iteration][transition_output.transition_name] += 1

    def update_init_iteration(self, person: 'Person'):
        self.state_counters[self.current_iteration][person.person_state.state.name] += 1

    def update_iteration_start(self, iteration: int):
        self.current_iteration = iteration
        self.state_counters.append(Counter())
        self.costs_counters.append(Cost())
        self.state_transition_counters.append(Counter())
        for state in self.model.states:
            self.state_counters[self.current_iteration][state.name] = 0

        for edge in EDGES:
            self.state_transition_counters[self.current_iteration][edge] = 0

    def update_iteration_end(self, iteration: int):
        if iteration == 0:
            with open(self.states_file_path, "a") as f:
                states = [k for k in self.state_counters[iteration].keys()]
                to_write = "week," + ",".join(states) + "\n"
                f.write(to_write)

            with open(self.costs_file_path, "a") as f:
                to_write = "week,direct,indirect_death,indirect_others,total\n"
                f.write(to_write)

            with open(self.state_transitions_file_path, "a") as f:
                transitions = [k for k in self.state_transition_counters[iteration].keys()]
                to_write = "week," + ",".join(transitions) + "\n"
                f.write(to_write)

        if not HEALTHY_ON_INIT:
            self.state_counters[self.current_iteration]["STATE_DEAD"] += self.all_dead

        self.save_history(iteration)
        if PLOT_HISTORY:
            self.plot_history(iteration)

        if iteration == NO_ITERATIONS:
            self.count_costs_summary()

        if iteration == NO_ITERATIONS and not PLOT_HISTORY:
            self.dynamic_plot = DynamicPlot(self.sim_id)
            self.plot_history(iteration)

    def count_costs_summary(self):
        total_costs_counter = Cost()
        for costs in self.costs_counters:
            total_costs_counter += costs
        print(total_costs_counter.to_dict())
        with open(self.costs_summary_file_path, "a") as f:
            f.write(str(total_costs_counter.to_dict()))
        with open(self.costs_summary_all_file_path, "a") as f:
            f.write(
                f"{self.sim_id},{total_costs_counter.direct},{total_costs_counter.total},{total_costs_counter.indirect_others},{total_costs_counter.indirect_death}\n")

    def update_counters(self, healthy, dead):
        self.state_counters[self.current_iteration]["STATE_HEALTHY"] += healthy
        self.state_counters[self.current_iteration]["STATE_DEAD"] += dead
        self.all_dead += dead

    def plot_history(self, iteration):
        self.dynamic_plot.update(iteration, self.state_counters, self.costs_counters, self.state_transition_counters)

    def save_history(self, iteration: int):
        occurences = [str(k) for k in self.state_counters[iteration].values()]
        with open(self.states_file_path, "a") as f:
            to_write = f"{iteration}," + ",".join(occurences) + "\n"
            f.write(to_write)

        with open(self.costs_file_path, "a") as f:
            costs = self.costs_counters[iteration]
            costs_str = [str(costs.direct), str(costs.indirect_death), str(costs.indirect_others), str(costs.total)]
            to_write = f"{iteration}," + ",".join(costs_str) + "\n"
            f.write(to_write)

        transitions = [str(k) for k in self.state_transition_counters[iteration].values()]
        with open(self.state_transitions_file_path, "a") as f:
            to_write = f"{iteration}," + ",".join(transitions) + "\n"
            f.write(to_write)
