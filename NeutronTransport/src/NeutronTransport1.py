import numpy as np


def free_flight_sampling(proba_per_ul):
    return - np.log(np.random.uniform()) / proba_per_ul


def simulate_transport(capture_scattering_ratio, sigma_total, wall_thickness, population_size):
    capture_probability = capture_scattering_ratio / (capture_scattering_ratio + 1)  # = S_c / (S_c + S_s)

    transmitted_amount = 0.0
    for i in range(population_size):
        # initial values for the incident beam
        position = 0.0
        director_cosine = 1.0

        while True:
            free_flight = director_cosine * free_flight_sampling(sigma_total)
            position += free_flight

            if position >= wall_thickness:
                transmitted_amount += 1
                break

            # scattering or capture
            if np.random.uniform() < capture_probability:
                break
            director_cosine = np.cos(np.random.uniform(low=0.0, high=np.pi))

    estimator = transmitted_amount / population_size
    variance = estimator * (1 - estimator)  # it's the value for a simple binary counter
    return estimator, variance
