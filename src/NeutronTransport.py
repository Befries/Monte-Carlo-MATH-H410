import numpy as np
import matplotlib.pyplot as plt


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

    while living_neutron > 0:
        # better estimator here + change sampling
        free_flight = free_flight_sampling(sigma_t, neutron_angle, living_neutron)
        neutron_position = np.sign(neutron_angle) * free_flight + neutron_position
        alive = neutron_position <= thickness

        neutron_position = neutron_position[alive]

        transmitted = living_neutron - np.size(neutron_position)
        living_neutron = living_neutron - transmitted
        passed += transmitted

        # better estimator for scattering & absorption + russian roulette?
        not_dead = (neutron_position >= 0) | interaction_sampling(p_absorption, living_neutron)
        neutron_position = neutron_position[not_dead]
        living_neutron = np.size(neutron_position)

        # splitting strategies

        # biasing strategies
        neutron_angle = np.random.uniform(low=-1, high=1, size=living_neutron)

        print(living_neutron)

    return passed / sample_size


proba = simulate_transport(500, 200, 0.1, int(1e5))

print(proba)
