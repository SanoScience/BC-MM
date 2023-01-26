from states import State
from history import PersonHistory
from config import ITERATIONS_PER_YEAR
import uuid


class Person:
    def __init__(self, state: State, time_in_state: int, age: int):
        self.uuid = str(uuid.uuid4())
        self.person_state = PersonState(state=state, time_in_state=time_in_state, age=age)
        self.history = PersonHistory(state=state, time_in_state=time_in_state, age=age)

    def step(self, iteration: int):
        transition_output = self.person_state.step(iteration)
        person_history_output = self.history.update(transition_output, iteration)
        return person_history_output


class PersonState:
    def __init__(self, state: State, time_in_state: int, age: int):
        self.state = state
        self.time_in_state = time_in_state
        self.time_in_stage = self.time_in_state
        self.age = age

    def step(self, iteration: int):
        if iteration % ITERATIONS_PER_YEAR == 0:
            self.age += 1

        transition_output = self.state.step(self, iteration)
        if transition_output.moved_to_new_state:
            if transition_output.moved_to_diagnosed:
                self.time_in_stage += 1
            else:
                self.time_in_stage = 1
            self.time_in_state = 1
            self.state = transition_output.state

        else:
            self.time_in_state += 1
            self.time_in_stage += 1

        return transition_output
