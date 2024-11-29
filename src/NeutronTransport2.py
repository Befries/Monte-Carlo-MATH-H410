import numpy as np


def free_flight_sampling(proba_per_ul, sample_size):
    return - np.log(np.random.uniform(size=sample_size)) / proba_per_ul


def split(positions, weights, m):
    return np.repeat(positions, m), np.repeat(weights / m, m)


def russian_roulette(weights, threshold):
    sample = np.random.uniform(size=weights.size)
    gun_loaded = weights < threshold
    trigger_safe = sample < threshold

    weights[gun_loaded & trigger_safe] = weights[gun_loaded & trigger_safe] / threshold
    return ~gun_loaded | trigger_safe


def simulate_transport(capture_scattering_ratio, sigma_total, wall_thickness, population_size, split_factor, threshold):
    capture_probability = capture_scattering_ratio / (capture_scattering_ratio + 1)  # = S_c / (S_c + S_s)
    split_frequency = 4

    estimator = 0
    second_estimator = 0  # estimator of the sum of square contributions
    for i in range(population_size):
        # initial values for the incident beam
        positions = np.zeros(1)
        weights = np.ones(1)
        director_cosine = np.ones(1)

        contribution = 0.0
        collision = 0

        while True:
            free_flight = director_cosine * free_flight_sampling(sigma_total, positions.size)
            positions += free_flight

            still_trapped = positions <= wall_thickness
            contribution += np.sum(weights, where=~still_trapped)

            weights = weights[still_trapped]
            positions = positions[still_trapped]

            scattered = np.random.uniform(size=positions.size) >= capture_probability
            positions = positions[scattered]
            weights = weights[scattered]

            if positions.size == 0:
                break

            if collision % split_frequency == 0:
                positions, weights = split(positions, weights, split_factor)
            elif (collision - 1) % split_frequency == 0:
                not_fucking_dead = russian_roulette(weights, threshold)
                positions = positions[not_fucking_dead]
                weights = weights[not_fucking_dead]

            collision += 1

            director_cosine = np.cos(np.random.uniform(low=0.0, high=np.pi, size=positions.size))

        estimator += contribution
        second_estimator += contribution ** 2

    estimator = estimator / population_size
    variance = second_estimator / population_size - estimator ** 2  # it's the value for a simple binary counter
    return estimator, variance

