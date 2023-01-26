from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import numpy as np
from config import rng, INDIRECT_DEATH_COST, DIRECT_YEARLY_COST_PER_STAGE, INDIRECT_OTHER_COSTS, ITERATIONS_PER_YEAR
from costs import Cost

if TYPE_CHECKING:
    from edges import Edge, EdgeComplementary
    from person import PersonState


class TransitionOutput:
    def __init__(self, state: 'State', moved_to_new_state=False, moved_to_diagnosed=False, from_state=None):
        self.moved_to_new_state = moved_to_new_state
        self.state = state
        self.moved_to_diagnosed = moved_to_diagnosed
        self.cost = Cost()
        self.from_state = from_state
        self.transition_name = f"{from_state.name.replace('STATE_','')}_{state.name.replace('STATE_','')}"


class State(ABC):
    def __init__(self):
        self.edges: list['Edge'] = []
        self.complementary_edge = None
        self.name = "STATE"

    def set_edges(self, edges: list['Edge'], complementary_edge: 'EdgeComplementary'):
        self.edges = edges
        self.complementary_edge = complementary_edge

    def step(self, person_state: 'PersonState', iteration) -> TransitionOutput:
        transition_state, is_same_state = self.step_next_state(person_state=person_state, iteration=iteration)
        tr_output = TransitionOutput(state=transition_state, moved_to_new_state=not is_same_state,
                                     from_state=person_state.state)
        if not is_same_state:
            tr_output.cost += transition_state.on_enter_cost()

        tr_output.cost += person_state.state.weekly_cost()
        return tr_output

    def on_enter_cost(self):
        return Cost()

    def weekly_cost(self):
        return Cost()

    def step_next_state(self, person_state: 'PersonState', iteration) -> tuple['State', bool]:
        assert self.complementary_edge is not None

        transition_states = []
        transition_probabilities = []
        for edge in self.edges:
            to_state, prob = edge.compute_transition_probability(person_state, iteration)
            transition_states.append(to_state)
            transition_probabilities.append(prob)

        to_state, prob = self.complementary_edge.compute_transition_probability(transition_probabilities)
        transition_states.append(to_state)
        transition_probabilities.append(prob)
        new_state, is_same_state = self.get_next_state(transition_states, transition_probabilities)
        return new_state, is_same_state

    def __repr__(self):
        return self.name

    @staticmethod
    def get_next_state(transition_states, transition_probabilities) -> tuple['State', bool]:
        next_state_idx = rng.multinomial(1, transition_probabilities)
        next_state_idx = np.argmax(next_state_idx)
        is_same_state = True if next_state_idx == len(transition_states) - 1 else False
        return transition_states[next_state_idx], is_same_state


class StateHealthy(State):
    def __init__(self):
        super(StateHealthy, self).__init__()
        self.name = "STATE_HEALTHY"

    def step(self, person_state: 'PersonState', iteration) -> TransitionOutput:
        transition_state, is_same_state = self.step_next_state(person_state=person_state, iteration=iteration)
        tr_output = TransitionOutput(state=transition_state, moved_to_new_state=not is_same_state,
                                     from_state=person_state.state)
        tr_output.cost += person_state.state.weekly_cost()
        return tr_output


class StateUndiagnosed(State):
    def __init__(self, stage: int):
        super(StateUndiagnosed, self).__init__()
        self.stage = stage
        self.name = f"STATE_UNDIAGNOSED_{self.stage}"

    def step(self, person_state: 'PersonState', iteration) -> TransitionOutput:
        transition_state, is_same_state = self.step_next_state(person_state=person_state, iteration=iteration)
        moved_to_diagnosed = True if "DIAGNOSED" in transition_state.name else False
        tr_output = TransitionOutput(state=transition_state, moved_to_new_state=not is_same_state,
                                     moved_to_diagnosed=moved_to_diagnosed, from_state=person_state.state)

        if not is_same_state:
            tr_output.cost += transition_state.on_enter_cost()
        tr_output.cost += person_state.state.weekly_cost()
        return tr_output


class StateDiagnosed(State):
    def __init__(self, stage: int):
        super(StateDiagnosed, self).__init__()
        self.stage = stage
        self.name = f"STATE_DIAGNOSED_{self.stage}"

    def weekly_cost(self):
        return Cost(direct=DIRECT_YEARLY_COST_PER_STAGE[self.stage] / ITERATIONS_PER_YEAR,
                    indirect_others=INDIRECT_OTHER_COSTS / ITERATIONS_PER_YEAR)


class StateDead(State):
    def __init__(self):
        super(StateDead, self).__init__()
        self.name = "STATE_DEAD"

    def on_enter_cost(self):
        return Cost(indirect_death=INDIRECT_DEATH_COST)
