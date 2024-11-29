# ma merde de base, ne s'en inspiré que pour comprendre pouquoi c'estun naufrage

import numpy as np


class NeutronPopulation:

    def __init__(self, pop_size):
        self.positions = np.zeros(pop_size)
        self.cosines = np.ones(pop_size)
        self.weights = np.ones(pop_size, dtype=np.float64)

        self.contributions = np.zeros(pop_size, dtype=np.float64)
        # start of each neutron descendant in the population
        self.descendant_indices = np.arange(0, pop_size, dtype=int)

    def size(self) -> int:
        return self.positions.size

    def clear_dead_neutron(self, living_criteria):
        has_legacy = np.diff(self.descendant_indices, append=self.positions.size) > 0
        cumulative_sizes = np.cumsum(np.add.reduceat(
            living_criteria.astype(int),
            np.minimum(self.descendant_indices, self.positions.size - 1), dtype=int) * has_legacy)
        self.descendant_indices = np.insert(cumulative_sizes[:-1], 0, 0)

        self.positions = self.positions[living_criteria]
        self.weights = self.weights[living_criteria]


def free_flight_sampling(proba_per_ul, cos_theta, sample_size) -> np.ndarray:
    """
    sample the distance traveled by a particle on its free flight along the x-axis
    :param proba_per_ul: the probability of interaction per unit length
    :param cos_theta: the director cosine of the neutron speed in the x direction
    :param sample_size: the size of the random sample needed
    :return: an array of distance randomly sampled according to the free flight PDF
    """
    sample = np.random.uniform(size=sample_size)
    return - np.log(sample) / proba_per_ul


def interaction_sampling(p_absorption, sample_size) -> np.ndarray:
    """
    an array of boolean deciding whether the interaction is an absorption or a scattering
    :param p_absorption: probability of absorption
    :param sample_size: the size of the random sample
    :return: false if an absorption occurred true if it is a scattering
    """
    sample = np.random.uniform(size=sample_size)
    return sample > p_absorption


def free_flight(n_population: NeutronPopulation, wall_thickness, sigma_t) -> (float, float):
    """

    :param n_population:
    :param wall_thickness:
    :param sigma_t:
    :return:
    """
    current_pop_size = n_population.size()
    free_flight_distance = free_flight_sampling(sigma_t, n_population.cosines, current_pop_size)
    n_population.positions = n_population.cosines * free_flight_distance + n_population.positions
    alive = n_population.positions <= wall_thickness

    # every prime neutron that still has descendants
    has_legacy = np.diff(n_population.descendant_indices, append=current_pop_size) > 0

    impact = (~alive).astype(int)
    # had the contribution of the descendants to their ancestor score
    # print(n_population.descendant_indices)
    sub_contrib = np.add.reduceat(
        n_population.weights * impact,
        np.minimum(n_population.descendant_indices, current_pop_size - 1)
    )
    n_population.contributions[has_legacy] += sub_contrib[has_legacy]

    # no neutron actually dies here in a free flight estimation, but need to put it for the basic algorithm
    n_population.clear_dead_neutron(alive)


def russian_roulette(n_population, threshold):
    sample = np.random.uniform(size=n_population.size())
    gun_loaded = n_population.weights < threshold
    trigger_safe = sample < threshold

    n_population.weights[gun_loaded & trigger_safe] = n_population.weights[gun_loaded & trigger_safe] / threshold
    return ~gun_loaded | trigger_safe


def split(neutron_population, splitting_factor):
    neutron_population.positions = np.repeat(neutron_population.positions, splitting_factor)
    neutron_population.weights = np.repeat(neutron_population.weights / splitting_factor, splitting_factor)
    neutron_population.descendant_indices *= splitting_factor


def simulate_transport(sigma_a, sigma_s, thickness, sample_size, splitting_factor, threshold):
    sigma_t = sigma_s + sigma_a
    p_absorption = sigma_a / sigma_t
    p_scattering = sigma_s / sigma_t
    neutron_population = NeutronPopulation(sample_size)

    iteration = 1

    while neutron_population.size() > 0:

        # free flight:
        free_flight(neutron_population, thickness, sigma_t)

        if neutron_population.size() <= 0:
            break

        # better estimator for scattering & absorption + russian roulette?
        not_dead = ((neutron_population.positions >= 0) &
                    interaction_sampling(p_absorption, neutron_population.size()))

        if iteration % 4 == 0:
            not_dead = not_dead & russian_roulette(neutron_population, threshold)

        neutron_population.clear_dead_neutron(not_dead)

        # splitting strategies
        if iteration % 2 == 0:
            split(neutron_population, splitting_factor)

        # biasing strategies
        neutron_population.cosines = np.cos(np.random.uniform(low=0, high=np.pi, size=neutron_population.size()))
        iteration += 1

    estimator = np.sum(neutron_population.contributions) / sample_size
    var_estimator = np.sum(neutron_population.contributions**2) / sample_size - estimator**2
    print(neutron_population.contributions)
    return estimator, var_estimator
