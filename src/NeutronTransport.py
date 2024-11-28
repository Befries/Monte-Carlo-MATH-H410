import numpy as np


class NeutronPopulation:

    def __init__(self, pop_size):
        self.positions = np.zeros(pop_size)
        self.cosines = np.ones(pop_size)
        self.weights = np.ones(pop_size)

        self.contributions = np.zeros(pop_size)
        # start of each neutron descendant in the population
        self.descendant_indices = np.arange(0, pop_size, dtype=int)

    def size(self) -> int:
        return self.positions.size

    def clear_dead_neutron(self, living_criteria):
        has_legacy = np.diff(self.descendant_indices, append=self.positions.size) > 0
        cumulative_sizes = np.cumsum(np.add.reduceat(
            living_criteria.astype(int),
            self.descendant_indices, dtype=int) * has_legacy)
        self.descendant_indices = np.insert(cumulative_sizes[:-1], 0, 0)

        self.positions = self.positions[living_criteria]
        self.weights = self.weights[living_criteria]
        self.descendant_indices[self.descendant_indices == self.positions.size] -= 1


def free_flight_sampling(proba_per_ul, cos_theta, sample_size) -> np.ndarray:
    """
    sample the distance traveled by a particle on its free flight along the x-axis
    :param proba_per_ul: the probability of interaction per unit length
    :param cos_theta: the director cosine of the neutron speed in the x direction
    :param sample_size: the size of the random sample needed
    :return: an array of distance randomly sampled according to the free flight PDF
    """
    sample = np.random.rand(sample_size)
    return -np.abs(cos_theta) / proba_per_ul * np.log(sample)


def interaction_sampling(p_absorption, sample_size) -> np.ndarray:
    """
    an array of boolean deciding whether the interaction is an absorption or a scattering
    :param p_absorption: probability of absorption
    :param sample_size: the size of the random sample
    :return: false if an absorption occurred true if it is a scattering
    """
    sample = np.random.rand(sample_size)
    return sample > p_absorption


def free_flight(n_population: NeutronPopulation, wall_thickness, sigma_t) -> (float, float):
    """

    :param n_population:
    :param wall_thickness:
    :param sigma_t:
    :return:
    """
    initial_pop_size = np.size(n_population.positions)
    free_flight_distance = free_flight_sampling(sigma_t, n_population.cosines, initial_pop_size)

    n_population.positions = np.sign(n_population.cosines) * free_flight_distance + n_population.positions
    alive = n_population.positions <= wall_thickness

    # every prime neutron that still has descendants
    has_legacy = np.diff(n_population.descendant_indices, append=n_population.size()) > 0

    # had the contribution of the descendants to their ancestor score
    # print(n_population.descendant_indices)
    sub_contrib = np.add.reduceat(
        n_population.weights * ~alive,
        n_population.descendant_indices
    )
    n_population.contributions[has_legacy] += sub_contrib[has_legacy]

    # no neutron actually dies here in a free flight estimation, but need to put it for the basic algorithm
    n_population.clear_dead_neutron(alive)


def simulate_transport(sigma_a, sigma_s, thickness, sample_size):
    sigma_t = sigma_s + sigma_a
    p_absorption = sigma_a / sigma_t
    neutron_population = NeutronPopulation(sample_size)

    while neutron_population.size() > 0:

        # free flight:
        free_flight(neutron_population, thickness, sigma_t)
        if neutron_population.size() <= 0:
            break

        # better estimator for scattering & absorption + russian roulette?
        not_dead = (neutron_population.positions >= 0) | interaction_sampling(p_absorption, neutron_population.size())
        neutron_population.clear_dead_neutron(not_dead)

        # splitting strategies

        # biasing strategies
        neutron_population.cosines = np.cos(np.random.uniform(low=0, high=np.pi, size=neutron_population.size()))

    estimator = np.sum(neutron_population.contributions) / sample_size
    var_estimator = np.sum(neutron_population.contributions**2) / sample_size - estimator**2
    return estimator, var_estimator