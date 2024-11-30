import numpy as np


def sample_antithetic(sample_size):
    if sample_size % 2 == 0:
        sample = np.random.uniform(size=sample_size // 2)
        return np.concatenate((sample, 1-sample))
    sample = np.random.uniform(size=sample_size//2 + 1)
    return np.concatenate((sample, 1-sample))[:-1]


def free_flight_sampling(positions, director_cosine, proba_per_ul, rest_estimation):
    sample = sample_antithetic(positions.size)
    return - np.log(1 - rest_estimation * sample) * director_cosine / proba_per_ul


def free_flight_estimator(positions, director_cosines, sigma_total, wall_thickness):
    return np.where(director_cosines > 0,
                    np.exp(np.clip(-sigma_total * (wall_thickness - positions)/director_cosines, -np.inf, 709)),
                    np.exp(np.clip(sigma_total * positions / director_cosines, -np.inf, 709))
                    )


def split(positions, weights, m):
    return np.repeat(positions, m), np.repeat(weights / m, m)


def russian_roulette(weights, threshold):
    sample = sample_antithetic(weights.size)
    gun_loaded = weights < threshold
    trigger_safe = sample < threshold

    survivor = gun_loaded & trigger_safe
    weights[survivor] = weights[survivor] / threshold
    return ~gun_loaded | trigger_safe


def simulate_transport(capture_scattering_ratio, sigma_total, wall_thickness, population_size, split_factor, threshold):
    scatter_probability = 1 / (capture_scattering_ratio + 1)
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

        while positions.size > 0:

            free_flight_estimate = free_flight_estimator(positions, director_cosine, sigma_total, wall_thickness)
            contribution += np.sum(weights * free_flight_estimate, where=director_cosine > 0)
            rest_estimation = 1 - free_flight_estimate
            weights *= scatter_probability * rest_estimation

            positions += free_flight_sampling(positions, director_cosine, sigma_total, rest_estimation)

            if collision % split_frequency == 0:
                not_fucking_dead = russian_roulette(weights, threshold)
                positions = positions[not_fucking_dead]
                weights = weights[not_fucking_dead]
                positions, weights = split(positions, weights, split_factor)

            collision += 1
            director_cosine = np.cos(sample_antithetic(positions.size)*np.pi)

        estimator += contribution
        second_estimator += contribution ** 2
    estimator = estimator / population_size
    variance = second_estimator / population_size - estimator ** 2  # it's the value for a simple binary counter
    return estimator, variance
