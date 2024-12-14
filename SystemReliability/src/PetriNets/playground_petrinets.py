import matplotlib.pyplot as plt
import time

from PetriNetSimulation import *
import PetriSystemEngineering as pse  # grouped all functions to build petri nets in a separate file


def acquire_characteristics():
    """
    function to test the algorithm
    """
    system, _ = pse.build_parallel_system([1.0], [1.0], reliability=True)
    # simulate system reliability over time for different mission durations
    population_size = 10000
    duration_sample_size = 10
    duration_samples = np.logspace(-1, 1, duration_sample_size)
    availability = np.empty_like(duration_samples)

    start = time.perf_counter()
    for i, duration in enumerate(duration_samples):
        availability[i] = 1 - system.run_simulation(duration, population_size)
    end = time.perf_counter()
    print(f"Simulation time: {end - start:.3f} seconds")

    plt.semilogx(duration_samples, availability)
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


t_performance()
