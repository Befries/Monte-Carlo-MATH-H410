import time

import numpy as np
from math import exp
from StateGraphEvolution import check_matrix


def treat(state_graph_matrix):
    total_rates_inv = -1 / state_graph_matrix.diagonal()
    pdf = (state_graph_matrix + np.diag(1 / total_rates_inv)) * total_rates_inv[:, np.newaxis]
    return total_rates_inv, pdf


def simulate_state_graph_evolution_system_based(state_graph_matrix: np.ndarray,
                                                fail_idx,
                                                sample_size,
                                                durations,
                                                reliability=False,
                                                failure_boost=1
                                                ):
    check_matrix(state_graph_matrix)
    # modify the state_graph_matrix based on the bias
    # deduce weights to multiply
    biased_matrix = state_graph_matrix - np.diag(state_graph_matrix.diagonal())
    biased_matrix[np.triu_indices(biased_matrix.shape[0])] *= failure_boost
    biased_matrix -= np.diag(np.sum(biased_matrix, axis=1))

    total_rates_inv, pdf = treat(state_graph_matrix)
    biased_rates_inv, biased_pdf = treat(biased_matrix)

    corrective_factor_exp = biased_rates_inv / total_rates_inv
    delta_rates = 1 / biased_rates_inv - 1 / total_rates_inv

    corrective_factor_discrete = pdf / biased_pdf

    biased_cdf = np.cumsum(biased_pdf, axis=1)

    max_duration_idx = len(durations)
    failed_at = np.zeros_like(durations)
    square_failed_at = np.zeros_like(durations)

    for i in range(sample_size):
        state = 0
        weight = 1.0
        working = True
        current_duration_idx = 0
        clock = 0.0

        while True:
            time_passed = np.random.exponential(biased_rates_inv[state])
            clock += time_passed

            while current_duration_idx < max_duration_idx and clock >= durations[current_duration_idx]:
                if not working:
                    failed_at[current_duration_idx] += weight
                    square_failed_at[current_duration_idx] += weight ** 2
                current_duration_idx += 1
            if current_duration_idx >= max_duration_idx:
                break

            weight *= corrective_factor_exp[state] * exp(delta_rates[state] * time_passed)

            next_state = np.searchsorted(biased_cdf[state, :], np.random.rand())
            weight *= corrective_factor_discrete[state, next_state]

            state = next_state
            working = state < fail_idx
            if reliability and not working:
                failed_at[current_duration_idx:] += weight
                square_failed_at[current_duration_idx:] += weight ** 2
                break

    estimation = 1 - failed_at / sample_size
    return estimation, square_failed_at / sample_size - (failed_at / sample_size) ** 2


def simulate_state_graph_reliability_cropped_pdf(state_graph_matrix: np.ndarray,
                                                 fail_idx,
                                                 sample_size,
                                                 durations,
                                                 inform=False
                                                 ):
    check_matrix(state_graph_matrix)
    # modify the state_graph_matrix based on the bias
    # deduce weights to multiply

    total_rates_inv, pdf = treat(state_graph_matrix)
    total_rates = 1 / total_rates_inv

    cdf = np.cumsum(pdf, axis=1)

    failed_at = np.zeros_like(durations)
    square_failed_at = np.zeros_like(durations)

    for i, duration in enumerate(durations):
        start = time.perf_counter()
        states = np.zeros(sample_size, dtype=np.int32)
        weights = np.ones(sample_size)
        clocks = np.zeros(sample_size)
        while states.size > 0:
            normalizer = 1 - np.exp(-total_rates[states] * (duration - clocks))
            clocks += - total_rates_inv[states] * np.log(1 - normalizer * np.random.rand(states.size))
            weights *= normalizer

            states = np.array([
                np.searchsorted(cdf_row, random_value)
                for cdf_row, random_value in zip(cdf[states], np.random.rand(states.size))
            ])

            failed = states >= fail_idx
            failed_at[i] += np.sum(weights[failed])
            square_failed_at[i] += np.sum(weights[failed] ** 2)

            states = states[~failed]
            weights = weights[~failed]
            clocks = clocks[~failed]

        if inform:
            print(time.perf_counter() - start)

    estimation = 1 - failed_at / sample_size
    return estimation, square_failed_at / sample_size - (failed_at / sample_size) ** 2
