import numpy as np


def sample_antithetic(sample_size):
    if sample_size % 2 == 0:
        sample = np.random.uniform(size=sample_size // 2)
        return np.concatenate((sample, 1 - sample))
    sample = np.random.uniform(size=sample_size // 2 + 1)
    return np.concatenate((sample, 1 - sample))[:-1]


def split(positions, weights, layers, m):
    return np.tile(positions, m), np.tile(weights / m, m), np.tile(layers, m)


def russian_roulette(weights, threshold):
    sample = sample_antithetic(weights.size)
    gun_loaded = weights < threshold
    trigger_safe = sample < threshold

    survivor = gun_loaded & trigger_safe
    weights[survivor] = weights[survivor] / threshold
    return ~gun_loaded | trigger_safe


def simulate_transport(wall_properties, population_size, split_factor, threshold, split_frequency=4):
    """

    :param wall_properties: Tuple of triplets containing: (absorb_scatter_ratio, sigma_t, thickness)
    :param population_size: Amount of incident neutrons to consider
    :param split_factor: Amount of child neutrons a parent splits into
    :param threshold: Value below which the russian roulette is activated
    :param split_frequency: Splits the neutron ever split_frequency collisions
    :return: An estimation of the transmission probability and the variance on a single neutron evaluation
    """
    # extract properties
    properties = np.asarray(wall_properties)
    sigma_t = properties[:, 1]
    scatter_probability = 1 / (properties[:, 0] + 1)
    thicknesses = properties[:, 2]
    layers_amount = np.size(thicknesses)
    optical_attenuation = np.exp(-sigma_t * thicknesses)  # e^(-sigma_t dx)

    # precomputes useful numbers
    post_layer_attenuation = [np.cumprod(optical_attenuation[i + 1:]) for i in range(layers_amount)]
    pre_layer_attenuation = ([np.array([])] +
                             [np.cumprod(optical_attenuation[i - 1::-1])[::-1] for i in range(1, layers_amount)])

    # the accumulation of the attenuation through the following layers
    post_layer_attenuation = np.asarray([np.pad(row, (layers_amount - len(row), 0),
                                                constant_values=0) for row in post_layer_attenuation])
    pre_layer_attenuation = np.asarray([np.pad(row, (0, layers_amount - len(row)),
                                               constant_values=0) for row in pre_layer_attenuation])
    np.fill_diagonal(post_layer_attenuation, 1)  # custom attenuation of current layer
    np.fill_diagonal(pre_layer_attenuation, 1)  # custom attenuation of current layer

    estimator = 0
    second_estimator = 0  # estimator of the sum of square contributions
    for i in range(population_size):
        # initial values for the incident beam
        positions = np.zeros(1)
        weights = np.ones(1)
        layers = np.zeros(1, dtype=int)
        director_cosine = np.ones(1)

        contribution = 0.0
        collision = 0

        while positions.size > 0:

            forward_neutron = director_cosine > 0.0
            backward_neutron = director_cosine <= 0.0

            # attenuation in the current layer if the neutron would travel to the beginning of the next / previous
            current_layer_optical_attenuation = np.empty_like(director_cosine)
            current_layer_optical_attenuation[forward_neutron] = (
                np.exp(-sigma_t[layers[forward_neutron]] *
                       (thicknesses[layers[forward_neutron]] - positions[forward_neutron])))
            current_layer_optical_attenuation[backward_neutron] = (
                np.exp(-sigma_t[layers[backward_neutron]] * positions[backward_neutron]))

            # adjust the attenuation possibly undergone in the voyage between layers
            adjusted_attenuation = np.empty(shape=(director_cosine.size, layers_amount))
            adjusted_attenuation[forward_neutron] = ((post_layer_attenuation[layers[forward_neutron]] *
                                                      current_layer_optical_attenuation[forward_neutron, np.newaxis])
                                                     ** (1 / director_cosine[forward_neutron, np.newaxis]))
            adjusted_attenuation[backward_neutron] = ((pre_layer_attenuation[layers[backward_neutron]] *
                                                       current_layer_optical_attenuation[backward_neutron, np.newaxis])
                                                      ** (-1 / director_cosine[backward_neutron, np.newaxis]))

            # estimation of a direct contribution from the current position of a neutron (if it goes forward)
            free_flight_estimate = np.where(
                director_cosine > 0.0,
                adjusted_attenuation[:, -1],
                adjusted_attenuation[:, 0]
            )
            # adds direct contribution of forward neutrons
            contribution += np.sum(weights * free_flight_estimate, where=director_cosine > 0)

            # sample the layer in which the neutron ends up
            def compute_new_layers():
                # the un-normalized layer probability:
                # (1 - attenuation) * attenuation of previous layers
                # = attenuation with layer i - attenuation until i - 1
                layer_probability = np.empty_like(adjusted_attenuation)
                layer_probability[forward_neutron] = - np.diff(adjusted_attenuation[forward_neutron], prepend=0)
                layer_probability[backward_neutron, -1] = adjusted_attenuation[backward_neutron, -1]
                layer_probability[backward_neutron, :-1] = (
                        adjusted_attenuation[backward_neutron, 1:] - adjusted_attenuation[backward_neutron, :-1])
                np.add.at(layer_probability, (np.arange(director_cosine.size), layers), 1)

                normalization_factor = 1 / (1 - free_flight_estimate)
                layer_sampler = sample_antithetic(layer_probability.shape[0])
                # sampling for every neutron, with different discrete CDF
                # takes the index of the first true
                return (layer_sampler[:, np.newaxis] < (np.cumsum(layer_probability, axis=1)
                                                        * normalization_factor[:, np.newaxis])).argmax(axis=1)

            new_layers = compute_new_layers()
            layer_variation = new_layers - layers
            layers = new_layers
            # updates the weights, scatter at arrival place
            weights *= scatter_probability[layers] * (1 - free_flight_estimate)

            # if arrived at a new layer, placed at edge
            positions[layer_variation > 0] = 0
            positions[layer_variation < 0] = thicknesses[layers[layer_variation < 0]]

            # free_flight limited inside the layer
            sample = sample_antithetic(positions.size)
            current_layer_optical_attenuation[layer_variation != 0] = optical_attenuation[layers[layer_variation != 0]]
            positions -= (np.log(1 - (1 - current_layer_optical_attenuation ** (1 / np.abs(director_cosine))) * sample)
                          * director_cosine / sigma_t[layers])

            if collision % split_frequency == 0:
                not_fucking_dead = russian_roulette(weights, threshold)
                positions = positions[not_fucking_dead]
                weights = weights[not_fucking_dead]
                layers = layers[not_fucking_dead]
                positions, weights, layers = split(positions, weights, layers, split_factor)

            collision += 1
            director_cosine = np.cos(sample_antithetic(positions.size) * np.pi)

        estimator += contribution
        second_estimator += contribution ** 2
    estimator = estimator / population_size
    variance = second_estimator / population_size - estimator ** 2  # it's the value for a simple binary counter
    return estimator, variance
