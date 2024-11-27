import numpy as np


def free_flight_sampling(coefficient, cos_theta, sample_size):
    # antithetic variables
    sample = np.random.rand(sample_size)
    return -np.abs(cos_theta) / coefficient * np.log(sample)


"""
return false if an absorption occurred
true if it is a scattering
"""
def interaction_sampling(p_absorption, sample_size):
    sample = np.random.rand(sample_size)
    return sample > p_absorption


def simulate_transport(sigma_a, sigma_s, thickness, sample_size):
    sigma_t = sigma_s + sigma_a
    living_neutron = sample_size
    neutron_position = np.zeros(sample_size)
    neutron_angle = np.ones(sample_size)

    p_absorption = sigma_a / sigma_t

    passed = 0
    variance_estimator = 0  # considers that result of each neutron = h(x_k)

    while living_neutron > 0:
        # better estimator here + change sampling
        free_flight = free_flight_sampling(sigma_t, neutron_angle, living_neutron)
        neutron_position = np.sign(neutron_angle) * free_flight + neutron_position
        alive = neutron_position <= thickness

        neutron_position = neutron_position[alive]

        transmitted = living_neutron - np.size(neutron_position)
        living_neutron = living_neutron - transmitted
        passed += transmitted
        variance_estimator += transmitted

        # better estimator for scattering & absorption + russian roulette?
        not_dead = (neutron_position >= 0) | interaction_sampling(p_absorption, living_neutron)
        neutron_position = neutron_position[not_dead]
        living_neutron = np.size(neutron_position)

        # splitting strategies

        # biasing strategies
        neutron_angle = np.cos(np.random.uniform(low=0, high=np.pi, size=living_neutron))

    estimation = passed / sample_size
    #  variance on the estimation D^2(I) = variance_estimation/N
    variance_estimation = variance_estimator / sample_size - estimation**2  # 1/n sum(h(x_k)^2) - I^2
    return estimation, variance_estimation

