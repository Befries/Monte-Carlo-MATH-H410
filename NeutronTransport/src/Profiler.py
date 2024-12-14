# Profiler
import numpy as np
import matplotlib.pyplot as plt
import time
import csv

from NeutronTransport1 import simulate_transport as st1
from NeutronTransport2 import simulate_transport as st2
from NeutronTransport3 import simulate_transport as st3
from NeutronTransport4 import simulate_transport as st4
from NeutronTransport5 import simulate_transport as st5


def test_thicknesses():
    thickness_tests = 100
    thicknesses = np.linspace(2, 10, thickness_tests)
    pop_size = int(1e4)
    penetrations = np.empty(thickness_tests)
    variances = np.empty(thickness_tests)
    simulation_time = np.empty(thickness_tests)

    for i, thickness in enumerate(thicknesses):
        start = time.perf_counter()
        penetrations[i], variances[i] = NeutronTransport3.simulate_transport(
            0.3,
            0.8,
            thickness,
            pop_size,
            20,
            0.01
        )
        simulation_time[i] = time.perf_counter() - start

    total_time = np.sum(simulation_time)
    efficiency = 1 / (variances * (simulation_time / pop_size))

    print("all simulation run in", total_time, "seconds")
    data = np.array([thicknesses, penetrations, variances, efficiency])
    np.savetxt("dataV3", data, delimiter=',')

    fig, axs = plt.subplots(2)
    axs[0].plot(thicknesses, penetrations)
    axs[0].set_title("penetration probability(V3)")
    axs[0].set_yscale('log')
    axs[0].set_xlabel("thickness [cm]")
    axs[0].grid(visible=True, which='both', axis='both')

    color = 'tab:red'
    axs[1].plot(thicknesses, efficiency, color=color)
    axs[1].set_title("Efficiency and Variance(V3)")
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


def test_ratio_crs(thick):
    pop_size = int(1e5)
    ratio_range_size = 100
    ratio_range = np.linspace(0.1, 0.6, ratio_range_size)
    penetrations = np.empty(ratio_range_size)
    variances = np.empty(ratio_range_size)

    for i, ratio in enumerate(ratio_range):
        start = time.perf_counter()
        penetrations[i], variances[i] = st1(
            ratio,
            0.8,
            thick,
            pop_size,
        )
    data = np.array([ratio_range, penetrations])
    np.savetxt("dataV1_ratio", data, delimiter=',')
    plt.plot(ratio_range, penetrations)
    plt.xlabel("ratio \u03A3\u2090/\u03A3\u209b")
    plt.title("penetration probability(V1)")
    plt.grid(visible=True, which='both', axis='both')
    plt.show()


def test_var_eff(version):
    thickness_tests = 10
    thicknesses = np.linspace(2, 10, thickness_tests)
    pop_size = int(1e4)
    penetrations1 = np.empty(thickness_tests)
    variances1 = np.empty(thickness_tests)
    simulation_time1 = np.empty(thickness_tests)

    for i, thickness in enumerate(thicknesses):
        start = time.perf_counter()
        penetrations1[i], variances1[i] = st1(
            0.3,
            0.8,
            thickness,
            pop_size

        )
        simulation_time1[i] = time.perf_counter() - start

    total_time1 = np.sum(simulation_time1)
    efficiency1 = 1 / (variances1 * (simulation_time1 / pop_size))

    print("all simulation run for v1 in", total_time1, "seconds")

    plt.figure(1)
    plt.plot(thicknesses, variances1, label='Version 1')
    plt.xlabel("thickness [cm]")
    plt.title(" Variance of simulation")
    plt.yscale('log')
    plt.grid(visible=True, which='both', axis='both')

    plt.figure(2)
    plt.plot(thicknesses, efficiency1, label='Version 1')
    plt.xlabel("thickness [cm]")
    plt.title(" efficiency of simulation")
    plt.yscale('log')
    plt.grid(visible=True, which='both', axis='both')

    if version >= 2:
        variances2 = np.empty(thickness_tests)
        penetrations2 = np.empty(thickness_tests)
        simulation_time2 = np.empty(thickness_tests)
        for i, thickness in enumerate(thicknesses):
            start = time.perf_counter()
            penetrations2[i], variances2[i] = st2(
                0.3,
                0.8,
                thickness,
                pop_size,
                20,
                0.01
            )
            simulation_time2[i] = time.perf_counter() - start

        total_time2 = np.sum(simulation_time2)
        efficiency2 = 1 / (variances2 * (simulation_time2 / pop_size))

        print("all simulation run for v2 in", total_time2, "seconds")
        plt.figure(1)
        plv = plt.plot(thicknesses, variances2, label='Version 2')
        plt.legend(plv, "version 2", loc='upper right')

        plt.figure(2)
        plt.plot(thicknesses, efficiency2, label='Version 2')

    if version >= 3:
        variances3 = np.empty(thickness_tests)
        penetrations3 = np.empty(thickness_tests)
        simulation_time3 = np.empty(thickness_tests)
        for i, thickness in enumerate(thicknesses):
            start = time.perf_counter()
            penetrations3[i], variances3[i] = st3(
                0.3,
                0.8,
                thickness,
                pop_size,
                20,
                0.01
            )
            simulation_time3[i] = time.perf_counter() - start

        total_time3 = np.sum(simulation_time3)
        efficiency3 = 1 / (variances3 * (simulation_time3 / pop_size))

        print("all simulation run for v3 in", total_time3, "seconds")
        plt.figure(1)
        plt.plot(thicknesses, variances3, label='Version 3')

        plt.figure(2)
        plt.plot(thicknesses, efficiency3, label='Version 3')

    if version >= 4:
        variances4 = np.empty(thickness_tests)
        penetrations4 = np.empty(thickness_tests)
        simulation_time4 = np.empty(thickness_tests)
        for i, thickness in enumerate(thicknesses):
            start = time.perf_counter()
            penetrations4[i], variances4[i] = st4(
                0.3,
                0.8,
                thickness,
                pop_size,
                20,
                0.01
            )
            simulation_time4[i] = time.perf_counter() - start

        total_time4 = np.sum(simulation_time4)
        efficiency4 = 1 / (variances4 * (simulation_time4 / pop_size))

        print("all simulation run for v4 in", total_time4, "seconds")
        plt.figure(1)
        plv = plt.plot(thicknesses, variances4, label='Version 4')

        plt.figure(2)
        plt.plot(thicknesses, efficiency4, label='Version 4')

    data = np.array([thicknesses, variances1, efficiency1, variances2, efficiency2, variances3, efficiency3])
    np.savetxt("data_all", data, delimiter=',')
    plt.legend()
    plt.show()


# test_var_eff(4)

def rplot_data(path_data):
    plot_data = []
    with open(path_data, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for line in csv_reader:
            plot_data.append(line)
    xval = plot_data[0]

    plt.figure(1)
    plt.xlabel("thickness [cm]")
    plt.title(" Variance of simulation")
    plt.yscale('log')
    plt.grid(visible=True, which='both', axis='both')

    plt.figure(2)
    plt.xlabel("thickness [cm]")
    plt.title(" efficiency of simulation")
    plt.yscale('log')
    plt.grid(visible=True, which='both', axis='both')
    for i in range(len(plot_data)):

        if (i % 2 == 0) and (i != 0):
            plt.figure(2)
            plt.plot(xval, plot_data[i])
        else:
            plt.figure(1)
            plt.plot(xval, plot_data[i])
    plt.show()


test_var_eff(3)
