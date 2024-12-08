import numpy as np
import matplotlib.pyplot as plt
import time

import NeutronTransport3
import NeutronTransport4
import NeutronTransport6
from NeutronTransport5 import simulate_transport


def test_thicknesses():
    thickness_tests = 15
    thicknesses = np.linspace(1, 15, thickness_tests)
    pop_size = int(1e4)
    penetrations = np.empty(thickness_tests)
    variances = np.empty(thickness_tests)
    simulation_time = np.empty(thickness_tests)

    for i, thickness in enumerate(thicknesses):
        start = time.perf_counter()
        penetrations[i], variances[i] = simulate_transport(
            ((0.3, 0.8, thickness * 3/8), (0.01, 1.4, thickness * 4/8), (0.6, 0.7, thickness * 1 / 8)),
            pop_size,
            20,
            1e-5
        )
        simulation_time[i] = time.perf_counter() - start

    total_time = np.sum(simulation_time)
    efficiency = 1 / (variances * (simulation_time / pop_size))

    print("all simulation run in", total_time, "seconds")

    fig, axs = plt.subplots(2)
    axs[0].semilogy(thicknesses, penetrations)
    axs[0].set_title("transmission probability")
    axs[0].set_xlabel("thickness [cm]")
    axs[0].grid(visible=True, which='both', axis='both')

    color = 'tab:red'
    axs[1].semilogy(thicknesses, efficiency, color=color)
    axs[1].set_title("Efficiency and Variance")
    axs[1].set_ylabel("Efficiency", color=color)
    axs[1].tick_params(axis='y', labelcolor=color)
    axs[1].set_xlabel("thickness [cm]")
    axs[1].grid(visible=True, which='both', axis='both')

    color = 'tab:blue'
    var_ax = axs[1].twinx()
    var_ax.semilogy(thicknesses, variances, color=color)
    var_ax.set_ylabel("Variance s²", color=color)
    var_ax.tick_params(axis='y', labelcolor=color)

    plt.tight_layout()
    plt.show()


def test_split():
    pop_size = int(1e3)
    split_range_size = 10
    threshold_range = np.linspace(0.001, 0.01, split_range_size)
    estimations = np.empty(split_range_size)
    variances = np.empty(split_range_size)
    simulation_time = np.empty(split_range_size)

    for i, split in enumerate(threshold_range):
        start = time.perf_counter()
        estimations[i], variances[i] = simulate_transport(
            0.3,
            0.8,
            10,
            pop_size,
            15,
            split
        )
        simulation_time[i] = time.perf_counter() - start

    total_time = np.sum(simulation_time)
    efficiency = 1 / (variances * (simulation_time / pop_size))

    print("all simulation run in", total_time, "seconds")
    fig, axs = plt.subplots(2)
    axs[0].scatter(threshold_range, variances)
    axs[0].set_title("variances")
    axs[0].set_yscale('log')
    axs[0].set_xlabel("split amount")
    axs[0].grid(visible=True, which='both', axis='both')

    color = 'tab:red'
    axs[1].plot(threshold_range, efficiency, color=color)
    axs[1].set_title("Efficiency")
    axs[1].set_ylabel("Efficiency", color=color)
    axs[1].tick_params(axis='y', labelcolor=color)
    axs[1].set_xlabel("split amount")
    axs[1].grid(visible=True, which='both', axis='both')

    plt.tight_layout()
    plt.show()


def test_thickness_multi_layer():
    thickness_tests = 15
    thicknesses = np.linspace(1, 15, thickness_tests)
    pop_size = int(1e5)
    penetrations = np.empty(thickness_tests)
    variances = np.empty(thickness_tests)
    simulation_time = np.empty(thickness_tests)

    for i, thickness in enumerate(thicknesses):
        start = time.perf_counter()
        penetrations[i], variances[i] = NeutronTransport6.simulate_transport(
            ((0.3, 0.8, thickness * 3/8), (0.01, 1.4, thickness * 4/8), (0.6, 0.7, thickness * 1 / 8)),
            pop_size
        )
        simulation_time[i] = time.perf_counter() - start
        print(simulation_time[i])

    total_time = np.sum(simulation_time)
    efficiency = 1 / (variances * (simulation_time / pop_size))

    print("all simulation run in", total_time, "seconds")

    data = np.asarray([thicknesses, penetrations, variances, efficiency, simulation_time])

    with open("NeutronTransport/data/multi_layer_test2.npy", 'wb') as f:
        np.save(f, data)

    plt.semilogy(thicknesses, penetrations)
    plt.title("transmission probability")
    plt.xlabel("thickness [cm]")
    plt.grid(visible=True, which='both', axis='both')
    plt.tight_layout()
    plt.show()


def plot_yes():
    with open("NeutronTransport/data/multi_layer_test.npy", 'rb') as f:
        data1 = np.load(f)

    with open("NeutronTransport/data/multi_layer_test2.npy", 'rb') as f:
        data2 = np.load(f)

    plt.semilogy(data1[0], data1[2], data2[0], data2[2])
    plt.title("Variance")
    plt.legend(("Variance reduction techniques", "simple counter and simple sampling"))
    plt.xlabel("thickness [cm]")
    plt.grid(visible=True, which='both', axis='both')
    plt.tight_layout()
    plt.show()


# test_thickness_multi_layer()
plot_yes()
