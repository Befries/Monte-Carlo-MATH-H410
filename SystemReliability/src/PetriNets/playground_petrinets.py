import numpy as np
import matplotlib.pyplot as plt
import time

from PetriComponents import *
from PetriNetSimulation import *


def build_1comp_petri(reliability=False) -> PetriNetSystem:
    system = PetriNetSystem()

    working = Place("component 1 working", starting_marking=1)
    system.add_place(working)
    failed = Place("component 1 failed")
    system.add_system_fail_place(failed)

    failure = SlowTransition("component 1 failure", transition_rate=1)
    system.add_transition(failure)
    failure.add_upstream(working)
    failure.add_downstream(failed)

    if reliability:
        return system

    repair = SlowTransition("component 1 repair", transition_rate=1)
    system.add_transition(repair)
    repair.add_upstream(failed)
    repair.add_downstream(working)

    return system


def acquire_characteristics():
    """
    function to test the algorithm
    """
    system = build_1comp_petri(reliability=False)

    # simulate system reliability over time for different mission durations
    population_size = 100000
    duration_sample_size = 10
    duration_samples = np.linspace(0.1, 5, duration_sample_size)
    availability = np.empty_like(duration_samples)

    start = time.perf_counter()
    for i, duration in enumerate(duration_samples):
        availability[i] = 1 - system.run_simulation(duration, population_size)
    end = time.perf_counter()
    print(f"Simulation time: {end - start:.3f} seconds")

    plt.plot(duration_samples, availability)
    plt.show()


acquire_characteristics()
