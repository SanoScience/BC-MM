import matplotlib.pyplot as plt
from config import NO_ITERATIONS, STATE_MARKERS, STATE_COLORS, COST_MARKERS, COST_COLORS, PATH_OUTPUT, \
    IS_COVID_SIMULATION, COVID_WEEKS, EDGES, FILTER_EDGES
import os


class DynamicPlot:
    min_x = 0
    max_x = NO_ITERATIONS

    def __init__(self, sim_id):
        self.sim_id = sim_id
        plt.ion()
        self.figure, self.ax = plt.subplots(nrows=1, ncols=5)
        title = "SIMULATION WITH COVID" if IS_COVID_SIMULATION else "SIMULATION NO COVID"
        self.figure.suptitle(title)
        self.figure.set_size_inches(20, 10)
        self.lines = {}
        for state in STATE_MARKERS.keys():
            marker = STATE_MARKERS[state]
            color = STATE_COLORS[state]
            if "HEALTHY" not in state and "DEAD" not in state:
                self.lines[state], = self.ax[1].plot([], [], marker=marker, color=color, label=state)
            else:
                self.lines[state], = self.ax[0].plot([], [], marker=marker, color=color, label=state)

        for cost in COST_MARKERS.keys():
            marker = COST_MARKERS[cost]
            color = COST_COLORS[cost]
            if "DIRECT" == cost:
                self.lines[cost], = self.ax[2].plot([], [], marker=marker, color=color, label=cost)
            elif "INDIRECT_OTHERS" == cost:
                self.lines[cost], = self.ax[3].plot([], [], marker=marker, color=color, label=cost)
            else:
                self.lines[cost], = self.ax[4].plot([], [], marker=marker, color=color, label=cost)

        # for edge in EDGES:
        #     self.lines[edge], = self.ax[4].plot([], [], label=edge)

        for ax in self.ax:
            ax.set_autoscaley_on(True)
            ax.set_xlim(self.min_x, self.max_x)
            ax.grid()

    def update(self, iteration, state_counters, costs_counters, state_transition_counters):
        self._update_state_counters(state_counters)
        self._update_costs_counters(costs_counters)
        # self._update_state_transition_counters(state_transition_counters)

        for i, ax in enumerate(self.ax):
            # if i < 4:
            ax.legend()
            ax.relim()
            ax.autoscale_view()
            ax.axvspan(COVID_WEEKS[0], COVID_WEEKS[-1], facecolor="gray", alpha=0.2)

        # box = self.ax[4].get_position()
        # self.ax[4].set_position([box.x0, box.y0, box.width * 0.8, box.height])
        # self.ax[4].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        # self.ax[4].relim()
        # self.ax[4].autoscale_view()
        # self.ax[4].axvspan(COVID_WEEKS[0], COVID_WEEKS[-1], facecolor="gray", alpha=0.2)

        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
        # if iteration == NO_ITERATIONS:
        #     plt.ioff()
        #     self.figure.savefig(os.path.join(PATH_OUTPUT, self.sim_id, "figure.png"), dpi=200)
        #     plt.show()

    def _update_state_counters(self, state_counters):
        states_count = {k: [dic[k] for dic in state_counters] for k in state_counters[0].keys()}
        xdata = range(len(states_count["STATE_HEALTHY"]))
        for state, ydata in states_count.items():
            self.lines[state].set_xdata(xdata)
            self.lines[state].set_ydata(ydata)

    def _update_costs_counters(self, costs_counters):
        costs_counts = {k: [dic.to_dict()[k] for dic in costs_counters] for k in costs_counters[0].to_dict().keys()}
        xdata = range(len(costs_counts["DIRECT"]))
        for cost, ydata in costs_counts.items():
            # ydata[0] = ydata[1]
            self.lines[cost].set_xdata(xdata)
            self.lines[cost].set_ydata(ydata)

    def _update_state_transition_counters(self, state_transition_counters):
        edges_count = {k: [dic[k] for dic in state_transition_counters] for k in state_transition_counters[0].keys()}
        xdata = range(len(edges_count["HEALTHY_DEAD"]))
        for edge, ydata in edges_count.items():
            if edge not in FILTER_EDGES:
                continue
            self.lines[edge].set_xdata(xdata)
            self.lines[edge].set_ydata(ydata)
