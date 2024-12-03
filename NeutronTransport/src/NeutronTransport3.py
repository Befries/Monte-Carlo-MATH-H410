import numpy as np


def free_flight_sampling(positions, director_cosine, proba_per_ul, rest_estimation):
    """
    
    :positions:
    :director_cosine:
    :proba_per_ul: 
    :rest_estimation: 
    :return: the free flight 
    """
    sample = np.random.uniform(size=positions.size)
    return - np.log(1 - rest_estimation * sample) * director_cosine / proba_per_ul


def free_flight_estimator(positions, director_cosines, sigma_total, wall_thickness):
    """
    This function performs the improved estimator. 

    :positions: current position of the neutron considered
    :director_cosines: direction of the current neutron 
    :sigma_total: proba of all interactions per unit lenght 
    :wall_thickness: wall thickness
    :return: improved estimator for neutrons going forward 
    """
    return np.where(director_cosines > 0,
                    np.exp(np.clip(-sigma_total * (wall_thickness - positions) / director_cosines, -np.inf, 709)),
                    np.exp(np.clip(sigma_total * positions / director_cosines, -np.inf, 709))
                    )


def split(positions, weights, m):
    """
    This function splits the neutrons. 

    :positions: position of the splitted neutron
    :weights: weight of the neutron splitted 
    :m: splitting factor 
    :return: position array with additional neutrons resulting from the splitting, weight array with additional neutrons resulting from the splitting
    """
    return np.tile(positions, m), np.tile(weights / m, m)


def russian_roulette(weights, threshold):
    """
    This function performs the Russian roulette.

    :weights: weight of the considered neutron
    :threshold: threshold 
    :return: False if the Russian roulette is not performed | True if the neutron survives to the Roussian roulette 
    """
    sample = np.random.uniform(size=weights.size)
    gun_loaded = weights < threshold
    trigger_safe = sample < threshold

    survivor = gun_loaded & trigger_safe
    weights[survivor] = weights[survivor] / threshold
    return ~gun_loaded | trigger_safe


def simulate_transport(capture_scattering_ratio, sigma_total, wall_thickness, population_size, split_factor, threshold):
     """
    This function simulates the neutron transport. 
    
    :capture_scattering_ratio: ratio between the proba of scattering and proba of capture
    :sigma_total: proba of any interaction per unit lenght
    :wall_thickness: wall thickness 
    :population_size: number of neutrons 
    :split_factor: split factor 
    :threshold: threfhold for the Russian roulette  
    :return:  improved estimation of the transmission probability, the variance associated 
    """
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
                positions = positions[not_fucking_dead] # updating the position of the neutrons that survived to the Russian roulette
                weights = weights[not_fucking_dead] # updating the weights of the neutrons that survived to the Russian roulette
                positions, weights = split(positions, weights, split_factor)

            collision += 1
            director_cosine = np.cos(np.random.uniform(low=0.0, high=np.pi, size=positions.size))

        estimator += contribution
        second_estimator += contribution ** 2
    estimator = estimator / population_size
    variance = second_estimator / population_size - estimator ** 2  # it's the value for a simple binary counter
    return estimator, variance
