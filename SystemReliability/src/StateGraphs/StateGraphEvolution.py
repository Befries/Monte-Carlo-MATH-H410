import numpy as np


def check_matrix(state_graph_matrix: np.ndarray):
    if np.linalg.norm(state_graph_matrix.sum(axis=1)) > 1e-14:
        raise ValueError("Invalid state graph matrix")


def simulate_state_graph_evolution_system_based(state_graph_matrix: np.ndarray,
                                                fail_idx,
                                                sample_size,
                                                durations,
                                                reliability=False
                                                ):
    check_matrix(state_graph_matrix)

    total_rates_inv = -1 / state_graph_matrix.diagonal()
    cdf = np.cumsum((state_graph_matrix + np.diag(1 / total_rates_inv)) * total_rates_inv[:, np.newaxis], axis=1)

    max_duration_idx = len(durations)
    working_at = np.zeros_like(durations)

    for i in range(sample_size):
        state = 0
        working = True
        current_duration_idx = 0
        clock = 0.0

        while True:
            clock += np.random.exponential(total_rates_inv[state])

            while current_duration_idx < max_duration_idx and clock >= durations[current_duration_idx]:
                working_at[current_duration_idx] += working
                current_duration_idx += 1
            if current_duration_idx >= max_duration_idx:
                break

            state = np.searchsorted(cdf[state, :], np.random.rand())
            working = state < fail_idx
            if reliability and not working:
                break

    estimation = working_at / sample_size
    return estimation, estimation * (1 - estimation)


def simulate_state_graph_evolution_component_based(state_graph_matrix: np.ndarray,
                                                   fail_idx,
                                                   sample_size,
                                                   durations,
                                                   reliability=False
                                                   ):
    check_matrix(state_graph_matrix)
    max_duration_idx = len(durations)
    working_at = np.zeros_like(durations)

    for i in range(sample_size):
        state = 0
        working = True
        current_duration_idx = 0
        clock = 0.0

        while True:
            next_state = state
            time_passed = 1e400  # = infinity

            for candidate in range(state_graph_matrix.shape[0]):
                if state_graph_matrix[state, candidate] == 0.0 or candidate == state:
                    continue
                candidate_time = np.random.exponential(1/state_graph_matrix[state, candidate])
                if candidate_time < time_passed:
                    next_state = candidate
                    time_passed = candidate_time
            clock += time_passed

            while current_duration_idx < max_duration_idx and clock >= durations[current_duration_idx]:
                working_at[current_duration_idx] += working
                current_duration_idx += 1
            if current_duration_idx >= max_duration_idx:
                break

            state = next_state
            working = state < fail_idx
            if reliability and not working:
                break

    estimation = working_at / sample_size
    return estimation, estimation * (1 - estimation)

# for three the three components system, the system based approach is 3 times faster, this can be expected
# to grow further with larger systems -> apply variance reduction to system-based
