from utils import lambda_from_five_year_death, lambda_from_dfs
import numpy as np
import random

SEED = 1013
random.seed(SEED)

# SIMULATION
IS_COVID_SIMULATION = True
HEALTHY_ON_INIT = False
PLOT_HISTORY = False

COVID_WEEKS = [i for i in range(9 + 52, 62 + 52)]
CRITICAL_COVID_WEEKS = []

ITERATIONS_PER_YEAR = 52
NO_ITERATIONS = 7 * ITERATIONS_PER_YEAR
START_YEAR = 2020
START_WEEK = 1
POPULATION_FRACTION = 0.01

MIN_AGE = 25
MAX_AGE = 85

PATH_OUTPUT = "../output/covid/" if IS_COVID_SIMULATION else "../output/non_covid"
COSTS_FILENAME = "costs.csv"
STATES_FILENAME = "states.csv"
STATE_TRANSITIONS_FILENAME = "state_transitions.csv"
COSTS_SUMMARY_FILE_NAME = "costs_summary.txt"
COSTS_SUMMARY_ALL_FILE_NAME = "covid_costs_summary_all.csv" if IS_COVID_SIMULATION else "non_covid_costs_summary_all.csv"
rng = np.random.default_rng(SEED)

WOMEN_BY_AGE = {25: int(1233777 * POPULATION_FRACTION), 30: int(1436161 * POPULATION_FRACTION),
                35: int(1596757 * POPULATION_FRACTION), 40: int(1502164 * POPULATION_FRACTION),
                45: int(1294636 * POPULATION_FRACTION), 50: int(1142203 * POPULATION_FRACTION),
                55: int(1234478 * POPULATION_FRACTION), 60: int(1460924 * POPULATION_FRACTION),
                65: int(1359815 * POPULATION_FRACTION), 70: int(1013368 * POPULATION_FRACTION),
                75: int(640118 * POPULATION_FRACTION), 80: int(581529 * POPULATION_FRACTION),
                85: int(583545 * POPULATION_FRACTION)}

POPULATION_SIZE = sum(WOMEN_BY_AGE.values())

S1_DIAG_PER_AGE = {25: int(461 * POPULATION_FRACTION), 30: int(1705 * POPULATION_FRACTION),
                   35: int(4069 * POPULATION_FRACTION), 40: int(7308 * POPULATION_FRACTION),
                   45: int(9287 * POPULATION_FRACTION), 50: int(10694 * POPULATION_FRACTION),
                   55: int(12375 * POPULATION_FRACTION), 60: int(17337 * POPULATION_FRACTION),
                   65: int(19713 * POPULATION_FRACTION), 70: int(11902 * POPULATION_FRACTION),
                   75: int(8417 * POPULATION_FRACTION), 80: int(6462 * POPULATION_FRACTION),
                   85: int(4752 * POPULATION_FRACTION), }

S2_DIAG_PER_AGE = {25: int(441 * POPULATION_FRACTION), 30: int(1630 * POPULATION_FRACTION),
                   35: int(3891 * POPULATION_FRACTION), 40: int(6989 * POPULATION_FRACTION),
                   45: int(8881 * POPULATION_FRACTION), 50: int(10227 * POPULATION_FRACTION),
                   55: int(11834 * POPULATION_FRACTION), 60: int(16579 * POPULATION_FRACTION),
                   65: int(18851 * POPULATION_FRACTION), 70: int(11382 * POPULATION_FRACTION),
                   75: int(8050 * POPULATION_FRACTION), 80: int(6179 * POPULATION_FRACTION),
                   85: int(4544 * POPULATION_FRACTION), }

S3_DIAG_PER_AGE = {25: int(102 * POPULATION_FRACTION), 30: int(377 * POPULATION_FRACTION),
                   35: int(900 * POPULATION_FRACTION), 40: int(1617 * POPULATION_FRACTION),
                   45: int(2055 * POPULATION_FRACTION), 50: int(2366 * POPULATION_FRACTION),
                   55: int(2738 * POPULATION_FRACTION), 60: int(3836 * POPULATION_FRACTION),
                   65: int(4361 * POPULATION_FRACTION), 70: int(2633 * POPULATION_FRACTION),
                   75: int(1862 * POPULATION_FRACTION), 80: int(1430 * POPULATION_FRACTION),
                   85: int(1051 * POPULATION_FRACTION), }

S4_DIAG_PER_AGE = {25: int(57 * POPULATION_FRACTION), 30: int(211 * POPULATION_FRACTION),
                   35: int(504 * POPULATION_FRACTION), 40: int(906 * POPULATION_FRACTION),
                   45: int(1151 * POPULATION_FRACTION), 50: int(1326 * POPULATION_FRACTION),
                   55: int(1534 * POPULATION_FRACTION), 60: int(2150 * POPULATION_FRACTION),
                   65: int(2444 * POPULATION_FRACTION), 70: int(1476 * POPULATION_FRACTION),
                   75: int(1044 * POPULATION_FRACTION), 80: int(801 * POPULATION_FRACTION),
                   85: int(589 * POPULATION_FRACTION), }

S1_UNDIAG_PER_AGE = {25: int(190 * POPULATION_FRACTION), 30: int(701 * POPULATION_FRACTION),
                     35: int(1674 * POPULATION_FRACTION), 40: int(3006 * POPULATION_FRACTION),
                     45: int(3820 * POPULATION_FRACTION), 50: int(4399 * POPULATION_FRACTION),
                     55: int(5090 * POPULATION_FRACTION), 60: int(7131 * POPULATION_FRACTION),
                     65: int(8109 * POPULATION_FRACTION), 70: int(4896 * POPULATION_FRACTION),
                     75: int(3462 * POPULATION_FRACTION), 80: int(2658 * POPULATION_FRACTION),
                     85: int(1955 * POPULATION_FRACTION), }
S1_UNDIAG_PER_AGE = S1_DIAG_PER_AGE

S2_UNDIAG_PER_AGE = {25: int(181 * POPULATION_FRACTION), 30: int(670 * POPULATION_FRACTION),
                     35: int(1600 * POPULATION_FRACTION), 40: int(2875 * POPULATION_FRACTION),
                     45: int(3653 * POPULATION_FRACTION), 50: int(4207 * POPULATION_FRACTION),
                     55: int(4868 * POPULATION_FRACTION), 60: int(6820 * POPULATION_FRACTION),
                     65: int(7754 * POPULATION_FRACTION), 70: int(4682 * POPULATION_FRACTION),
                     75: int(3311 * POPULATION_FRACTION), 80: int(2542 * POPULATION_FRACTION),
                     85: int(1869 * POPULATION_FRACTION), }

S3_UNDIAG_PER_AGE = {25: int(42 * POPULATION_FRACTION), 30: int(155 * POPULATION_FRACTION),
                     35: int(370 * POPULATION_FRACTION), 40: int(665 * POPULATION_FRACTION),
                     45: int(845 * POPULATION_FRACTION), 50: int(973 * POPULATION_FRACTION),
                     55: int(1126 * POPULATION_FRACTION), 60: int(1578 * POPULATION_FRACTION),
                     65: int(1794 * POPULATION_FRACTION), 70: int(1083 * POPULATION_FRACTION),
                     75: int(766 * POPULATION_FRACTION), 80: int(588 * POPULATION_FRACTION),
                     85: int(432 * POPULATION_FRACTION), }

S4_UNDIAG_PER_AGE = {25: int(24 * POPULATION_FRACTION), 30: int(87 * POPULATION_FRACTION),
                     35: int(208 * POPULATION_FRACTION), 40: int(373 * POPULATION_FRACTION),
                     45: int(474 * POPULATION_FRACTION), 50: int(545 * POPULATION_FRACTION),
                     55: int(631 * POPULATION_FRACTION), 60: int(884 * POPULATION_FRACTION),
                     65: int(1005 * POPULATION_FRACTION), 70: int(607 * POPULATION_FRACTION),
                     75: int(429 * POPULATION_FRACTION), 80: int(330 * POPULATION_FRACTION),
                     85: int(242 * POPULATION_FRACTION), }

for age, number in S1_DIAG_PER_AGE.items():
    WOMEN_BY_AGE[age] -= number
for age, number in S2_DIAG_PER_AGE.items():
    WOMEN_BY_AGE[age] -= number
for age, number in S3_DIAG_PER_AGE.items():
    WOMEN_BY_AGE[age] -= number
for age, number in S4_DIAG_PER_AGE.items():
    WOMEN_BY_AGE[age] -= number

for age, number in S1_UNDIAG_PER_AGE.items():
    WOMEN_BY_AGE[age] -= number
for age, number in S2_UNDIAG_PER_AGE.items():
    WOMEN_BY_AGE[age] -= number
for age, number in S3_UNDIAG_PER_AGE.items():
    WOMEN_BY_AGE[age] -= number
for age, number in S4_UNDIAG_PER_AGE.items():
    WOMEN_BY_AGE[age] -= number

WOMEN_BY_AGE_YEARLY = {}
for age5, number in WOMEN_BY_AGE.items():
    for i in range(5):
        WOMEN_BY_AGE_YEARLY[age5 + i] = WOMEN_BY_AGE[age5] // 5

DIAG_PER_AGE = [S1_DIAG_PER_AGE, S2_DIAG_PER_AGE, S3_DIAG_PER_AGE, S4_DIAG_PER_AGE, ]
UNDIAG_PER_AGE = [S1_UNDIAG_PER_AGE, S2_UNDIAG_PER_AGE, S3_UNDIAG_PER_AGE, S4_UNDIAG_PER_AGE]

# PLOTTING
STATE_MARKERS = {
    "STATE_HEALTHY": ".",
    "STATE_DEAD": ",",
    "STATE_UNDIAGNOSED_1": "2",
    "STATE_UNDIAGNOSED_2": "3",
    "STATE_UNDIAGNOSED_3": "4",
    "STATE_UNDIAGNOSED_4": "+",
    "STATE_DIAGNOSED_1": "2",
    "STATE_DIAGNOSED_2": "3",
    "STATE_DIAGNOSED_3": "4",
    "STATE_DIAGNOSED_4": "+",
}
STATE_COLORS = {
    "STATE_HEALTHY": "g",
    "STATE_DEAD": "r",
    "STATE_UNDIAGNOSED_1": "#0083cc",
    "STATE_UNDIAGNOSED_2": "#006299",
    "STATE_UNDIAGNOSED_3": "#005280",
    "STATE_UNDIAGNOSED_4": "#004266",
    "STATE_DIAGNOSED_1": "#cc9c00",
    "STATE_DIAGNOSED_2": "#997500",
    "STATE_DIAGNOSED_3": "#806200",
    "STATE_DIAGNOSED_4": "#664e00",
}

COST_MARKERS = {
    "DIRECT": "4",
    "TOTAL": ".",
    "INDIRECT_OTHERS": "+",
    "INDIRECT_DEATH": "x"
}

COST_COLORS = {
    "DIRECT": "g",
    "TOTAL": "b",
    "INDIRECT_OTHERS": "y",
    "INDIRECT_DEATH": "r"
}

EDGES = ['HEALTHY_DEAD', 'HEALTHY_UNDIAGNOSED_1', 'HEALTHY_HEALTHY', 'UNDIAGNOSED_1_DIAGNOSED_1', 'UNDIAGNOSED_1_DEAD',
         'UNDIAGNOSED_1_UNDIAGNOSED_2', 'UNDIAGNOSED_1_UNDIAGNOSED_1', 'UNDIAGNOSED_2_DIAGNOSED_2',
         'UNDIAGNOSED_2_DEAD', 'UNDIAGNOSED_2_UNDIAGNOSED_3', 'UNDIAGNOSED_2_UNDIAGNOSED_2',
         'UNDIAGNOSED_3_DIAGNOSED_3', 'UNDIAGNOSED_3_DEAD', 'UNDIAGNOSED_3_UNDIAGNOSED_4',
         'UNDIAGNOSED_3_UNDIAGNOSED_3', 'UNDIAGNOSED_4_DIAGNOSED_4', 'UNDIAGNOSED_4_DEAD',
         'UNDIAGNOSED_4_UNDIAGNOSED_4', 'DIAGNOSED_1_HEALTHY', 'DIAGNOSED_1_DEAD', 'DIAGNOSED_1_DIAGNOSED_2',
         'DIAGNOSED_1_DIAGNOSED_1', 'DIAGNOSED_2_HEALTHY', 'DIAGNOSED_2_DEAD', 'DIAGNOSED_2_DIAGNOSED_3',
         'DIAGNOSED_2_DIAGNOSED_2', 'DIAGNOSED_3_HEALTHY', 'DIAGNOSED_3_DEAD', 'DIAGNOSED_3_DIAGNOSED_4',
         'DIAGNOSED_3_DIAGNOSED_3', 'DIAGNOSED_4_HEALTHY', 'DIAGNOSED_4_DEAD', 'DIAGNOSED_4_DIAGNOSED_4', 'DEAD_DEAD']

FILTER_EDGES = ['DIAGNOSED_2_HEALTHY', 'DIAGNOSED_2_DEAD', 'DIAGNOSED_2_DIAGNOSED_3']

# STATES
NO_CANCER_STATES = 4
DEATH_PROB_BY_AGE = {
    25: 0.000250, 26: 0.000250, 27: 0.000260, 28: 0.000280, 29: 0.000300, 30: 0.000320, 31: 0.000350, 32: 0.000380,
    33: 0.000410, 34: 0.000450, 35: 0.000500, 36: 0.000550, 37: 0.000600, 38: 0.000660, 39: 0.000730, 40: 0.000800,
    41: 0.000890, 42: 0.001000, 43: 0.001130, 44: 0.001270, 45: 0.001440, 46: 0.001610, 47: 0.001800, 48: 0.002000,
    49: 0.002200, 50: 0.002410, 51: 0.002640, 52: 0.002880, 53: 0.003170, 54: 0.003500, 55: 0.003890, 56: 0.004340,
    57: 0.004850, 58: 0.005430, 59: 0.006060, 60: 0.006720, 61: 0.007390, 62: 0.008080, 63: 0.008800, 64: 0.009580,
    65: 0.010440, 66: 0.011370, 67: 0.012390, 68: 0.013490, 69: 0.014690, 70: 0.016030, 71: 0.017520, 72: 0.019210,
    73: 0.021050, 74: 0.023120, 75: 0.025370, 76: 0.027760, 77: 0.030370, 78: 0.033380, 79: 0.037100, 80: 0.041860,
    81: 0.047940, 82: 0.055640, 83: 0.064630, 84: 0.074410, 85: 0.084530, 86: 0.094710, 87: 0.104970, 88: 0.115630,
    89: 0.127110, 90: 0.139620, 91: 0.153860, 92: 0.169070, 93: 0.185280, 94: 0.202470, 95: 0.220650, 96: 0.239790,
    97: 0.259880, 98: 0.280880, 99: 0.302760, 100: 0.325460, 101: 0.325460, 102: 0.325460, 103: 0.325460, 104: 0.325460,
    105: 0.325460, 106: 0.325460, 107: 0.325460, 108: 0.325460, 109: 0.325460, }

DECADE_CANCER_PROB_BY_AGE = {20: 0.001, 30: 0.005, 40: 0.015, 50: 0.024, 60: 0.035, 70: 0.041, 80: 0.03, 90: 0.03,
                             100: 0.03}
FIVE_YEAR_SURV_BY_STAGE_DIAGNOSED = {1: 0.975, 2: 0.856, 3: 0.44, 4: 0.23, }

FIVE_YEAR_SURV_BY_STAGE_UNDIAGNOSED = {1: 0.97, 2: 0.84, 3: 0.37, 4: 0.14}

FIVE_YEAR_DEATH_BY_STAGE_DIAGNOSED = {stage: 1 - fys for stage, fys in FIVE_YEAR_SURV_BY_STAGE_DIAGNOSED.items()}

FIVE_YEAR_DEATH_BY_STAGE_UNDIAGNOSED = {stage: 1 - fys for stage, fys in FIVE_YEAR_SURV_BY_STAGE_UNDIAGNOSED.items()}

FIVE_YEAR_DEATH_BY_STAGE_DIAGNOSED_COVID = {1: 0.027, 2: 0.158, 3: 0.614, 4: 0.844, }

FIVE_YEAR_DEATH_LAMBDAS_DIAGNOSED_NONCOVID = {stage: lambda_from_five_year_death(fyd) for stage, fyd in
                                              FIVE_YEAR_DEATH_BY_STAGE_DIAGNOSED.items()}
FIVE_YEAR_DEATH_LAMBDAS_DIAGNOSED_COVID = {stage: lambda_from_five_year_death(fyd) for stage, fyd in
                                           FIVE_YEAR_DEATH_BY_STAGE_DIAGNOSED_COVID.items()}

FIVE_YEAR_DEATH_LAMBDAS_UNDIAGNOSED = {stage: lambda_from_five_year_death(fyd) for stage, fyd in
                                       FIVE_YEAR_DEATH_BY_STAGE_UNDIAGNOSED.items()}

MEAN_TIME_STAGE_UNDIAGNOSED = {1: 2, 2: 1.5, 3: 1, 4: 0.5}
MEAN_TIME_STAGE_DIAGNOSED = {1: 2.5, 2: 2, 3: 1.5, 4: 1}
STANDARD_DEVIATION_STAGE_DIAGNOSED = {state: 1 for state, mt in MEAN_TIME_STAGE_DIAGNOSED.items()}
STANDARD_DEVIATION_STAGE_UNDIAGNOSED = {state: 1 for state, mt in MEAN_TIME_STAGE_UNDIAGNOSED.items()}

A_STAGE_UNDIAGNOSED = {1: 0.000001, 2: 0.000002, 3: 0.000003, 4: 0.000004}
A_STAGE_DIAGNOSED = {1: 0.000005, 2: 0.000006, 3: 0.000007, 4: 0.000008}
A_STAGE_UNDIAGNOSED = {1: 20, 2: 25, 3: 30, 4: 40}
A_STAGE_DIAGNOSED = {1: 10, 2: 15, 3: 20, 4: 25}

DFS_STAGE_NONCOVID = {1: 0.987, 2: 0.873, 3: 0.52, 4: 0.037}
DFS_STAGE_COVID = {1: 0.801, 2: 0.708, 3: 0.422, 4: 0.03}
LAMBDA_DFS_STAGE_NONCOVID = {stage: lambda_from_dfs(dfs) for stage, dfs in DFS_STAGE_NONCOVID.items()}
LAMBDA_DFS_STAGE_COVID = {stage: lambda_from_dfs(dfs) for stage, dfs in DFS_STAGE_COVID.items()}

YEARLY_DIAGNOSIS_NON_COVID = 0.124
YEARLY_DIAGNOSIS_COVID = 0.116

# COSTS
DIRECT_YEARLY_COST_PER_STAGE = {1: 1880, 2: 3185, 3: 5573, 4: 7869}
INDIRECT_DEATH_COST = 123564
INDIRECT_OTHER_COSTS = 13159
