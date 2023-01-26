from abc import ABC, abstractmethod
from typing import Tuple

from config import (DEATH_PROB_BY_AGE, ITERATIONS_PER_YEAR, DECADE_CANCER_PROB_BY_AGE,
                    FIVE_YEAR_DEATH_LAMBDAS_DIAGNOSED_NONCOVID, FIVE_YEAR_DEATH_LAMBDAS_DIAGNOSED_COVID,
                    FIVE_YEAR_DEATH_LAMBDAS_UNDIAGNOSED, IS_COVID_SIMULATION,
                    YEARLY_DIAGNOSIS_COVID, YEARLY_DIAGNOSIS_NON_COVID, LAMBDA_DFS_STAGE_COVID,
                    LAMBDA_DFS_STAGE_NONCOVID, COVID_WEEKS, CRITICAL_COVID_WEEKS, A_STAGE_DIAGNOSED,
                    A_STAGE_UNDIAGNOSED)
from person import PersonState
from states import State
from utils import exponential_cumulative_distribution, exponential_distribution


class Edge(ABC):
    def __init__(self, from_state: State, to_state: State):
        self.from_state = from_state
        self.to_state = to_state
        self.edge_name = f"{from_state.name.replace('STATE_','')}_{to_state.name.replace('STATE_','')}"

    @abstractmethod
    def compute_transition_probability(self, person_state: PersonState, iteration) -> Tuple[State, float]:
        return self.to_state, 0


class EdgeComplementary(Edge):
    def __init__(self, from_state: State, to_state: State):
        super(EdgeComplementary, self).__init__(from_state, to_state)

    def compute_transition_probability(self, other_edges_probabilities: list[float]) -> Tuple[State, float]:
        transition_probability = 1. - sum(other_edges_probabilities)
        return self.to_state, transition_probability


class EdgeHealthyDead(Edge):
    def __init__(self, from_state: State, to_state: State):
        super(EdgeHealthyDead, self).__init__(from_state, to_state)

    def compute_transition_probability(self, person_state: PersonState, iteration) -> Tuple[State, float]:
        transition_probability = self.get_transition_probability_by_age(person_state.age)
        return self.to_state, transition_probability

    @staticmethod
    def get_transition_probability_by_age(age):
        yearly_prob = DEATH_PROB_BY_AGE[age]
        return yearly_prob / ITERATIONS_PER_YEAR


class EdgeHealthyCancer(Edge):
    def __init__(self, from_state: State, to_state: State):
        super(EdgeHealthyCancer, self).__init__(from_state, to_state)

    def compute_transition_probability(self, person_state: PersonState, iteration) -> Tuple[State, float]:
        transition_probability = self.get_transition_probability_by_age(person_state.age)
        return self.to_state, transition_probability

    @staticmethod
    def get_transition_probability_by_age(age):
        decade_prob = DECADE_CANCER_PROB_BY_AGE[(age // 10) * 10]
        yearly_prob = decade_prob / 10
        return yearly_prob / ITERATIONS_PER_YEAR


class EdgeUndiagnosedDiagnosed(Edge):
    def __init__(self, from_state: State, to_state: State, state: int):
        super(EdgeUndiagnosedDiagnosed, self).__init__(from_state, to_state)
        self.state = state

    def compute_transition_probability(self, person_state: PersonState, iteration) -> Tuple[State, float]:
        transition_probability = self._get_transition_probability(person_state.age, iteration)
        return self.to_state, transition_probability

    def _get_transition_probability(self, age, iteration):
        if IS_COVID_SIMULATION and iteration in COVID_WEEKS:
            if iteration in CRITICAL_COVID_WEEKS:
                prob = 0
            else:
                prob = YEARLY_DIAGNOSIS_COVID / ITERATIONS_PER_YEAR
        else:
            prob = YEARLY_DIAGNOSIS_NON_COVID / ITERATIONS_PER_YEAR
        return prob


class EdgeUndiagnosedUndiagnosedPlus1(Edge):
    name = "EdgeUndiagnosedUndiagnosedPlus1"

    def __init__(self, from_state: State, to_state: State, state: int):
        super(EdgeUndiagnosedUndiagnosedPlus1, self).__init__(from_state, to_state)
        self.state = state

    def compute_transition_probability(self, person_state: PersonState, iteration) -> Tuple[State, float]:
        transition_probability = self.get_transition_probability(person_state.time_in_state, self.state)
        return self.to_state, transition_probability

    @staticmethod
    def get_transition_probability(time_in_state, state):
        return exponential_cumulative_distribution(t=time_in_state / ITERATIONS_PER_YEAR,
                                                     l=A_STAGE_UNDIAGNOSED[state]) * 0.0009

class EdgeUndiagnosedDead(Edge):
    name = "EdgeUndiagnosedDead"

    def __init__(self, from_state: State, to_state: State, state: int):
        super(EdgeUndiagnosedDead, self).__init__(from_state, to_state)
        self.state = state

    def compute_transition_probability(self, person_state: PersonState, iteration) -> Tuple[State, float]:
        transition_probability = self.get_transition_probability(person_state.time_in_state, self.state)
        return self.to_state, transition_probability

    @staticmethod
    def get_transition_probability(time_in_state, state):
        prob_t = exponential_cumulative_distribution(t=time_in_state / ITERATIONS_PER_YEAR,
                                                     l=FIVE_YEAR_DEATH_LAMBDAS_UNDIAGNOSED[state])

        absolute_probability = prob_t / (ITERATIONS_PER_YEAR*5)
        return absolute_probability


class EdgeDiagnosedHealthy(Edge):
    name = "EdgeDiagnosedHealthy"

    def __init__(self, from_state: State, to_state: State, state: int):
        super(EdgeDiagnosedHealthy, self).__init__(from_state, to_state)
        self.state = state

    def compute_transition_probability(self, person_state: PersonState, iteration) -> Tuple[State, float]:
        transition_probability = self.get_transition_probability(person_state.time_in_stage, self.state, iteration)
        return self.to_state, transition_probability

    @staticmethod
    def get_transition_probability(time_in_stage, state, iteration=1):
        if IS_COVID_SIMULATION and iteration in COVID_WEEKS:
            lam = LAMBDA_DFS_STAGE_COVID[state]
        else:
            lam = LAMBDA_DFS_STAGE_NONCOVID[state]

        prob_t = exponential_distribution(t=time_in_stage / ITERATIONS_PER_YEAR, l=lam) / (5 * ITERATIONS_PER_YEAR)
        return prob_t / 3


class EdgeDiagnosedDiagnosedPlus1(Edge):
    name = "EdgeDiagnosedDiagnosedPlus1"

    def __init__(self, from_state: State, to_state: State, state: int):
        super(EdgeDiagnosedDiagnosedPlus1, self).__init__(from_state, to_state)
        self.state = state

    def compute_transition_probability(self, person_state: PersonState, iteration) -> Tuple[State, float]:
        transition_probability = self.get_transition_probability(person_state.time_in_stage, self.state)
        return self.to_state, transition_probability

    @staticmethod
    def get_transition_probability(time_in_stage, state):
        return exponential_cumulative_distribution(t=time_in_stage / ITERATIONS_PER_YEAR,
                                                     l=A_STAGE_DIAGNOSED[state]) * 0.0009

class EdgeDiagnosedDead(Edge):
    name = "EdgeDiagnosedDead"

    def __init__(self, from_state: State, to_state: State, state: int):
        super(EdgeDiagnosedDead, self).__init__(from_state, to_state)
        self.state = state

    def compute_transition_probability(self, person_state: PersonState, iteration) -> Tuple[State, float]:
        transition_probability = self.get_transition_probability(person_state.time_in_stage, self.state, iteration)
        return self.to_state, transition_probability

    @staticmethod
    def get_transition_probability(time_in_stage, state, iteration=1):
        if IS_COVID_SIMULATION and iteration in COVID_WEEKS:
            lam = FIVE_YEAR_DEATH_LAMBDAS_DIAGNOSED_COVID[state]
        else:
            lam = FIVE_YEAR_DEATH_LAMBDAS_DIAGNOSED_NONCOVID[state]
        prob_t = exponential_cumulative_distribution(t=time_in_stage / ITERATIONS_PER_YEAR,
                                                     l=lam)

        absolute_probability = prob_t / (ITERATIONS_PER_YEAR*5)
        return absolute_probability
