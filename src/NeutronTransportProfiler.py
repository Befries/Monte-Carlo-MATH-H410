import numpy as np
import matplotlib.pyplot as plt
import time

from NeutronTransport3 import simulate_transport


def test_thicknesses():
    thickness_tests = 8
    thicknesses = np.linspace(2, 10, thickness_tests)
    pop_size = int(1e3)
    penetrations = np.empty(thickness_tests)
    variances = np.empty(thickness_tests)
    simulation_time = np.empty(thickness_tests)

    for i, thickness in enumerate(thicknesses):
        start = time.perf_counter()
        penetrations[i], variances[i] = simulate_transport(
            0.3,
            0.8,
            thickness,
            pop_size,
            20,
            0.0001
        )
        simulation_time[i] = time.perf_counter() - start

    total_time = np.sum(simulation_time)
    efficiency = 1 / (variances * (simulation_time / pop_size))

    print("all simulation run in", total_time, "seconds")

    fig, axs = plt.subplots(2)
    axs[0].scatter(thicknesses, penetrations)
    axs[0].set_title("penetration probability")
    axs[0].set_yscale('log')
    axs[0].set_xlabel("thickness [cm]")
    axs[0].grid(visible=True, which='both', axis='both')

    color = 'tab:red'
    axs[1].plot(thicknesses, efficiency, color=color)
    axs[1].set_title("Efficiency and Variance")
    axs[1].set_ylabel("Efficiency", color=color)
    axs[1].tick_params(axis='y', labelcolor=color)
    axs[1].set_xlabel("thickness [cm]")
    axs[1].grid(visible=True, which='both', axis='x')

    color = 'tab:blue'
    var_ax = axs[1].twinx()
    var_ax.scatter(thicknesses, variances, color=color)
    var_ax.set_yscale('log')
    var_ax.set_ylabel("Variance s²", color=color)
    var_ax.tick_params(axis='y', labelcolor=color)
    var_ax.grid(visible=True, which='both')

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


test_thicknesses()
