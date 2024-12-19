import matplotlib.pyplot as plt
import time

import PetriSystemEngineering as pse  # grouped all functions to build petri nets in a separate file
import numpy as np


def acquire_characteristics():
    """
    function to test the algorithm
    """
    start = time.perf_counter()
    system, cost_place = pse.build_obsolescence_strategy_k_net(4, 2, 3, 1, 50, 5, 20)
    print(f"system built in {time.perf_counter() - start} seconds")
    # simulate system reliability over time for different mission durations
    population_size = 10000
    duration_sample_size = 20
    mission_time = 100
    duration_samples = np.logspace(-1, np.log10(mission_time), duration_sample_size)
    cost = np.empty_like(duration_samples)
    cost_variance = np.empty_like(duration_samples)

    mean_sojourn_failure = np.empty_like(duration_samples)
    sojourn_failure_variance = np.empty_like(duration_samples)

    start = time.perf_counter()
    for i, duration in enumerate(duration_samples):
        cost[i], cost_variance[i] = system.run_simulation(duration, population_size)
        mean_sojourn_failure[i] = system.system_fail_place.mean_sojourn_time
        sojourn_failure_variance[i] = system.system_fail_place.sojourn_time_variance
    end = time.perf_counter()
    print(f"Simulation time: {end - start:.3f} seconds")

    fig, axs = plt.subplots(2)
    axs[0].semilogx(duration_samples, cost / duration_samples)
    axs[0].set_title("Cost per unit of time")
    axs[1].semilogx(duration_samples, np.sqrt(cost_variance/population_size))
    axs[1].set_title("Standard deviation")
    plt.tight_layout()
    plt.show()


def t_performance():
    rates = []
    rates_amount = 10
    elapsed = []

    for i in range(rates_amount):
        rates.append(1.0)
        system, _ = pse.build_parallel_system(rates, rates, reliability=False)
        start = time.perf_counter()
        print(1 - system.run_simulation(10, 10000))
        elapsed.append(time.perf_counter() - start)

    plt.plot(range(rates_amount), elapsed)
    plt.show()


acquire_characteristics()
