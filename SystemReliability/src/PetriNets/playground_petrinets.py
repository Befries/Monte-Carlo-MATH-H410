import matplotlib.pyplot as plt
import time

from PetriNetSimulation import *
import PetriSystemEngineering as pse  # grouped all functions to build petri nets in a separate file


def acquire_characteristics():
    """
    function to test the algorithm
    """
    system, _ = pse.build_parallel_system([1.0, 1.0], [1.0, 1.0], reliability=False)
    # simulate system reliability over time for different mission durations
    population_size = 10000
    duration_sample_size = 10
    duration_samples = np.logspace(0, 1.6, duration_sample_size)
    availability = np.empty_like(duration_samples)
    mean_sojourn_failure = np.empty_like(duration_samples)

    start = time.perf_counter()
    for i, duration in enumerate(duration_samples):
        availability[i] = 1 - system.run_simulation(duration, population_size)
        mean_sojourn_failure[i] = system.system_fail_place.mean_sojourn_time
    end = time.perf_counter()
    print(f"Simulation time: {end - start:.3f} seconds")

    fig, axs = plt.subplots(2)
    axs[0].semilogx(duration_samples, mean_sojourn_failure)
    axs[0].set_title("Mean Sojourn Time")
    axs[1].semilogx(duration_samples, availability)
    axs[1].set_title("Availability")
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
