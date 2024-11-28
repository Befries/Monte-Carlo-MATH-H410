import numpy as np


class NeutronPopulation:

    def __init__(self, pop_size):
        self.positions = np.zeros(pop_size)
        self.cosines = np.ones(pop_size)
        self.weights = np.ones(pop_size)

    def size(self) -> int:
        return self.positions.size


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
    n_population.positions = n_population.positions[alive]

    # change that part to account for better estimator, take weights into account
    sub_estimator = initial_pop_size - np.size(n_population.positions)
    sub_var_estimator = sub_estimator  # for the moment (1^2 = 1 so don't need to do fancy stuff for now)
    return sub_estimator, sub_var_estimator


def simulate_transport(sigma_a, sigma_s, thickness, sample_size):
    sigma_t = sigma_s + sigma_a
    p_absorption = sigma_a / sigma_t

    estimator = 0
    var_estimator = 0

    neutron_population = NeutronPopulation(sample_size)

    while neutron_population.size() > 0:

        # free flight:
        current_estimator, current_var_estimator = free_flight(neutron_population, thickness, sigma_t)
        estimator += current_estimator  # I += I_i
        var_estimator += current_var_estimator - current_estimator**2 / sample_size  # D^2(I) += D^2(I_i)

        # better estimator for scattering & absorption + russian roulette?
        not_dead = (neutron_population.positions >= 0) | interaction_sampling(p_absorption, neutron_population.size())
        neutron_population.positions = neutron_population.positions[not_dead]

        # splitting strategies

        # biasing strategies
        neutron_population.cosines = np.cos(np.random.uniform(low=0, high=np.pi, size=neutron_population.size()))

    return estimator / sample_size, var_estimator / sample_size

