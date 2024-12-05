import numpy as np


def free_flight_sampling(proba_per_ul):
    """
    This function performs the sample of the free flight probability.

    :proba_per_ul: total proba of interaction
    :return: sampling of the free flight
    """
    return - np.log(np.random.uniform()) / proba_per_ul


def simulate_transport(wall_properties, population_size):

    properties = np.asarray(wall_properties)
    capture_probability = properties[:, 0] / (properties[:, 0] + 1)
    sigma_t = properties[:, 1]
    thickness = properties[:, 2]

    transmitted_amount = 0.0  # number of transmitted neutron to the right side of the wall
    for i in range(population_size):
        # initial values for the incident beam
        position = 0.0
        director_cosine = 1.0
        layer = 0

        while True:
            free_flight = director_cosine * free_flight_sampling(sigma_t[layer])
            position += free_flight
            if position >= thickness[layer]:
                layer += 1
                position = 0
                if layer == thickness.size:
                    transmitted_amount += 1
                    break
                continue
            elif position <= 0:
                layer -= 1
                position = thickness[layer]
                if layer == -1:
                    break
                continue

            if np.random.uniform() < capture_probability[layer]:
                break

            director_cosine = np.cos(np.random.uniform(low=0.0, high=np.pi))

    estimator = transmitted_amount / population_size
    variance = estimator * (1 - estimator)  # it's the value for a simple binary counter
    return estimator, variance