import numpy as np
from math import erf, sqrt


def lambda_from_five_year_death(fys):
    return -np.log(1 - fys) / 5


def lambda_from_dfs(dfs):
    return -np.log(dfs) / 5


def exponential_cumulative_distribution(t, l=0.5):
    return 1 - np.exp(l * (-t))


def exponential_distribution(t, l=0.5):
    return np.exp(l * (-t))


def log_normal_cumulative_distribution(t, mean=1, sigma=0.5):
    return 0.5 * (1 + erf((np.log(t) - mean) / (sigma * sqrt(2))))
