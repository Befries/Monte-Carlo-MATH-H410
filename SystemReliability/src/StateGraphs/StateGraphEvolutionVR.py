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
    delta_rates = 1/biased_rates_inv - 1/total_rates_inv

    corrective_factor_discrete = pdf / biased_pdf

    biased_cdf = np.cumsum(biased_pdf, axis=1)

    max_duration_idx = len(durations)
    working_at = np.zeros_like(durations)
    square_working_at = np.zeros_like(durations)

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
                    working_at[current_duration_idx] += weight
                    square_working_at[current_duration_idx] += weight ** 2
                current_duration_idx += 1
            if current_duration_idx >= max_duration_idx:
                break

            weight *= corrective_factor_exp[state] * exp(delta_rates[state] * time_passed)

            next_state = np.searchsorted(biased_cdf[state, :], np.random.rand())
            weight *= corrective_factor_discrete[state, next_state]

            state = next_state
            working = state < fail_idx
            if reliability and not working:
                working_at[current_duration_idx:] += weight
                square_working_at[current_duration_idx:] += weight ** 2
                break

    estimation = 1 - working_at / sample_size
    return estimation, square_working_at / sample_size - (working_at/sample_size) ** 2


