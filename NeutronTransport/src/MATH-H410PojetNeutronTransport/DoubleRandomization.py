import numpy as np
import NeutronTransport6
import NeutronTransport4


def uncertain_properties_simulation(
        central_capture_scattering_ratio,
        fluctuation_capture_scattering_ratio,
        central_sigma_total,
        fluctuation_sigma_total,
        wall_thickness,
        thickness_fluctuation,
        layer_quantity_range):
    """
    This function simulates the neutron transport with uncertain properties of the materials.
    The amount of layers is chosen from the layer_quantity_range parameter, then the various properties
    are chosen from a normal distribution with the given central values and standard variations

    :param central_capture_scattering_ratio: central value of the capture scattering ratio
    :param fluctuation_capture_scattering_ratio: standard deviation of the capture scattering ratio
    :param central_sigma_total: central value of the sigma total
    :param fluctuation_sigma_total: standard deviation of the sigma total
    :param wall_thickness: thickness of the wall
    :param thickness_fluctuation: standard deviation of the layer thickness
    :param layer_quantity_range: range of possible layer quantities
    """
    layer_amount = np.random.choice(layer_quantity_range)
    print(f"{layer_amount} layers with ", end="")
    capture_scattering_ratio = np.abs(np.random.normal(central_capture_scattering_ratio,
                                                       fluctuation_capture_scattering_ratio,
                                                       layer_amount))
    sigma_total = np.abs(np.random.normal(central_sigma_total,
                                          fluctuation_sigma_total,
                                          layer_amount))
    # ensures that the total thickness is indeed wall_thickness with random layer dimensions
    thickness = np.abs(np.random.normal(wall_thickness / layer_amount,
                                        thickness_fluctuation,
                                        size=layer_amount))
    thickness = thickness / np.sum(thickness) * wall_thickness
    properties = np.asarray((capture_scattering_ratio, sigma_total, thickness)).T
    pop_size = int(1e6)
    transmission_probability, variance = NeutronTransport6.simulate_transport(properties, pop_size)
    return transmission_probability, variance


t2 = 0
v2 = 0

average_sample_size = 20
for i in range(average_sample_size):
    estimator, variance = uncertain_properties_simulation(
        0.3,
        0.05,
        0.6,
        0.1,
        10,
        1,
        range(3, 8)
    )
    t2 += estimator
    v2 += variance
    print(f"done {i}")

t2 /= average_sample_size
v2 /= average_sample_size

print(f"transmission probability {t2} and standard deviation {np.sqrt(v2 / int(1e6))}")

# returns the expected transition probability for a wall with the central values as parameters
t1, v1 = NeutronTransport4.simulate_transport(0.3,
                                              0.6,
                                              10,
                                              10000,
                                              15,
                                              1e-4)
print(f"expected transmission probability {t1} and standard deviation {np.sqrt(v1 / 10000)}")
