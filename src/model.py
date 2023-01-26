from states import StateHealthy, StateUndiagnosed, StateDiagnosed, StateDead
from edges import (EdgeComplementary, EdgeHealthyDead, EdgeHealthyCancer, EdgeUndiagnosedUndiagnosedPlus1,
                   EdgeUndiagnosedDiagnosed, EdgeUndiagnosedDead, EdgeDiagnosedHealthy, EdgeDiagnosedDiagnosedPlus1,
                   EdgeDiagnosedDead)
from config import NO_CANCER_STATES


class Model:
    def __init__(self):
        self.state_healthy = StateHealthy()
        self.states_undiagnosed = [StateUndiagnosed(i + 1) for i in range(NO_CANCER_STATES)]
        self.states_diagnosed = [StateDiagnosed(i + 1) for i in range(NO_CANCER_STATES)]
        self.state_dead = StateDead()
        self.states = [self.state_healthy, *self.states_undiagnosed, *self.states_diagnosed, self.state_dead]
        self.edges = []
        state_healthy_edges = [
            EdgeHealthyDead(from_state=self.state_healthy, to_state=self.state_dead),
            EdgeHealthyCancer(from_state=self.state_healthy, to_state=self.states_undiagnosed[0])
        ]
        self.edges += state_healthy_edges
        state_healthy_complementary_edge = EdgeComplementary(from_state=self.state_healthy, to_state=self.state_healthy)
        self.edges.append(state_healthy_complementary_edge)
        self.state_healthy.set_edges(edges=state_healthy_edges, complementary_edge=state_healthy_complementary_edge)

        for i, state_undiagnosed in enumerate(self.states_undiagnosed):
            state_undiagnosed_edges = [
                EdgeUndiagnosedDiagnosed(from_state=state_undiagnosed, to_state=self.states_diagnosed[i], state=i + 1),
                EdgeUndiagnosedDead(from_state=state_undiagnosed, to_state=self.state_dead, state=i + 1)
            ]
            if i + 1 < len(self.states_undiagnosed):
                state_undiagnosed_edges.append(EdgeUndiagnosedUndiagnosedPlus1(from_state=state_undiagnosed,
                                                                               to_state=self.states_undiagnosed[i + 1],
                                                                               state=i + 1))
            state_undiagnosed_complementary_edge = EdgeComplementary(from_state=state_undiagnosed,
                                                                     to_state=state_undiagnosed)
            state_undiagnosed.set_edges(edges=state_undiagnosed_edges,
                                        complementary_edge=state_undiagnosed_complementary_edge)
            self.edges += state_undiagnosed_edges
            self.edges.append(state_undiagnosed_complementary_edge)

        for i, state_diagnosed in enumerate(self.states_diagnosed):
            state_diagnosed_edges = [
                EdgeDiagnosedHealthy(from_state=state_diagnosed, to_state=self.state_healthy, state=i + 1),
                EdgeDiagnosedDead(from_state=state_diagnosed, to_state=self.state_dead, state=i + 1)
            ]
            if i + 1 < len(self.states_diagnosed):
                state_diagnosed_edges.append(EdgeDiagnosedDiagnosedPlus1(from_state=state_diagnosed,
                                                                         to_state=self.states_diagnosed[i + 1],
                                                                         state=i + 1))

            state_diagnosed_complementary_edge = EdgeComplementary(from_state=state_diagnosed,
                                                                   to_state=state_diagnosed)
            state_diagnosed.set_edges(edges=state_diagnosed_edges,
                                      complementary_edge=state_diagnosed_complementary_edge)

            self.edges += state_diagnosed_edges
            self.edges.append(state_diagnosed_complementary_edge)

        edge_dead = EdgeComplementary(from_state=self.state_dead, to_state=self.state_dead)
        self.state_dead.set_edges(edges=[], complementary_edge=edge_dead)
        self.edges.append(edge_dead)
