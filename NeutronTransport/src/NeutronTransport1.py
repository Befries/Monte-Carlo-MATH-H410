import numpy as np


def free_flight_sampling(proba_per_ul):
    """
    This function performs the sample of the free flight probability. 
    
    :proba_per_ul: total proba of interaction
    :return: sampling of the free flight
    """
    return - np.log(np.random.uniform()) / proba_per_ul


def simulate_transport(capture_scattering_ratio, sigma_total, wall_thickness, population_size):
    """
    This function simulates the neutron transport. 
    
    :capture_scattering_ratio: ratio between the proba of scattering and proba of capture
    :sigma_total: proba of any interaction per unit lenght
    :wall_thickness: wall thickness 
    :population_size: number of neutrons 
    :return:estimation of the transmission probability, the variance associated 
    """
    capture_probability = capture_scattering_ratio / (capture_scattering_ratio + 1)  # = S_c / (S_c + S_s)

    transmitted_amount = 0.0  # number of transmitted neutron to the right side of the wall
    for i in range(population_size):
        # initial values for the incident beam
        position = 0.0
        director_cosine = 1.0

        while True:
            free_flight = director_cosine * free_flight_sampling(sigma_total)
            position += free_flight

            if position >= wall_thickness:  # if the neutron escapes from the wall the loop stops
                transmitted_amount += 1
                break

            # scattering or capture
            if np.random.uniform() < capture_probability or position < 0.0:
                break
            director_cosine = np.cos(np.random.uniform(low=0.0, high=np.pi))

    estimator = transmitted_amount / population_size
    variance = estimator * (1 - estimator)  # it's the value for a simple binary counter
    return estimator, variance
