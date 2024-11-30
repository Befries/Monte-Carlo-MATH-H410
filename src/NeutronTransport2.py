import numpy as np


def free_flight_sampling(proba_per_ul, sample_size):
    return - np.log(np.random.uniform(size=sample_size)) / proba_per_ul


def russian_roulette(sample_size, general_weight, threshold):
    sample = np.random.uniform(size=sample_size)
    trigger_safe = sample < threshold
    return trigger_safe


def simulate_transport(capture_scattering_ratio, sigma_total, wall_thickness, population_size, split_factor, threshold):
    capture_probability = capture_scattering_ratio / (capture_scattering_ratio + 1)  # = S_c / (S_c + S_s)
    split_frequency = 4

    estimator = 0
    second_estimator = 0  # estimator of the sum of square contributions
    for i in range(population_size):
        # initial values for the incident beam
        positions = np.zeros(1)
        director_cosine = np.ones(1)

        contribution = 0.0
        collision = 0
        general_weight = 1.0

        while True:
            free_flight = director_cosine * free_flight_sampling(sigma_total, positions.size)
            positions += free_flight

            transmitted = positions > wall_thickness
            contribution += np.count_nonzero(transmitted) * general_weight

            not_dead = ~(transmitted | (positions < 0)) & (np.random.uniform(size=positions.size) >= capture_probability)
            positions = positions[not_dead]

            if positions.size == 0:
                break

            if collision % split_frequency == 0:
                not_fucking_dead = russian_roulette(positions.size, general_weight, threshold)
                if general_weight < threshold:
                    general_weight = general_weight / threshold
                    positions = positions[not_fucking_dead]
                positions = np.repeat(positions, split_factor)
                general_weight = general_weight / split_factor


            collision += 1
            director_cosine = np.cos(np.random.uniform(low=0.0, high=np.pi, size=positions.size))

        estimator += contribution
        second_estimator += contribution ** 2

    estimator = estimator / population_size
    variance = second_estimator / population_size - estimator ** 2  # it's the value for a simple binary counter
    return estimator, variance

