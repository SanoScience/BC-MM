import random

from tqdm import tqdm

from config import (NO_ITERATIONS, IS_COVID_SIMULATION, WOMEN_BY_AGE, MAX_AGE,
                    DIAG_PER_AGE, UNDIAG_PER_AGE, HEALTHY_ON_INIT, rng, WOMEN_BY_AGE_YEARLY)
from history import GlobalHistory
from model import Model
from person import Person
import uuid
from edges import EdgeHealthyCancer, EdgeHealthyDead


class Simulation:
    def __init__(self):
        self.sim_id = str(uuid.uuid4())
        self.model = Model()
        self.global_history = GlobalHistory(model=self.model, sim_id=self.sim_id)
        self.population = []
        self._init_population()
        if not HEALTHY_ON_INIT:
            self.current_healthy = WOMEN_BY_AGE_YEARLY

    def start(self):
        if IS_COVID_SIMULATION:
            print("Starting simulation WITH Covid...")
        else:
            print("Starting simulation WITHOUT Covid...")

        print(f"SIMULATION ID: {self.sim_id}")

        for iteration in tqdm(range(1, NO_ITERATIONS + 1)):
            self.global_history.update_iteration_start(iteration)
            for person in self.population:
                person_history_output = person.step(iteration)
                self.global_history.update(person_history_output)

            if not HEALTHY_ON_INIT:
                self.add_diseased_from_healthy(iteration)

            self.global_history.update_iteration_end(iteration)
        self.on_stop()

    def on_stop(self):
        print("Simulation finished.")

    def _init_population(self):
        self.global_history.update_iteration_start(0)

        if HEALTHY_ON_INIT:
            for age5, women in WOMEN_BY_AGE.items():
                if age5 > MAX_AGE:
                    continue
                for i in range(5):
                    for j in range(women // 5):
                        new_person = Person(self.model.state_healthy, random.randint(1, 26), age5 + i)
                        self.population.append(new_person)
                        self.global_history.add_person_history(new_person)
        else:
            self.global_history.update_counters(sum(WOMEN_BY_AGE.values()), 0)

        for s, undiag_per_age in enumerate(UNDIAG_PER_AGE):
            for age5, women in undiag_per_age.items():
                if age5 > MAX_AGE:
                    continue
                for i in range(5):
                    for j in range(women // 5):
                        new_person = Person(self.model.states_undiagnosed[s], random.randint(1, 156), age5 + i)
                        self.population.append(new_person)
                        self.global_history.add_person_history(new_person)

        for s, diag_per_age in enumerate(DIAG_PER_AGE):
            for age5, women in diag_per_age.items():
                if age5 > MAX_AGE:
                    continue
                for i in range(5):
                    for j in range(women // 5):
                        new_person = Person(self.model.states_diagnosed[s], random.randint(1, 156), age5 + i)
                        self.population.append(new_person)
                        self.global_history.add_person_history(new_person)

        self.global_history.update_iteration_end(0)

    def add_diseased_from_healthy(self, iteration):
        new_healthy = {}
        n_dead_all = 0
        for age, number in self.current_healthy.items():
            prob_cancer = EdgeHealthyCancer.get_transition_probability_by_age(age)
            prob_dead = EdgeHealthyDead.get_transition_probability_by_age(age)
            n_new_states = rng.multinomial(number, [prob_cancer, prob_dead, 1 - (prob_dead + prob_cancer)])
            n_cancer = n_new_states[0]
            n_dead = n_new_states[1]
            n_dead_all += n_dead

            for i in range(n_cancer):
                self.add_person(self.model.states_undiagnosed[0], 1, age)

            new_healthy[age] = max(number - n_cancer - n_dead, 0)
            #new_healthy[age] = max(number, 0)
        self.global_history.update_counters(healthy=sum(new_healthy.values()), dead=n_dead_all)
        self.current_healthy = new_healthy

    def add_person(self, state, time_in_state, age):
        new_person = Person(state, time_in_state, age)
        self.population.append(new_person)
        self.global_history.add_person_history(new_person)
