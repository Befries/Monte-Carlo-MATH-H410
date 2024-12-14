import numpy as np
import matplotlib.pyplot as plt
import time

from PetriComponents import *
from PetriNetSimulation import *


def build_1comp_petri(index,
                      reliability=False,
                      fail_message=False,
                      failure_rate=1.0,
                      repair_rate=1.0,
                      instantaneous=False,
                      element_name="component"
                      ):
    """
    build a simple petri net of one component with the two states "working" and "failed"
    :param index: an index for the component
    :param reliability: if it follows a reliability design (no repair for this component)
    :param fail_message: (optional) whether to create a message associated with this component failure
    :param failure_rate: lambda
    :param repair_rate: mu
    :param instantaneous: if the transitions are instantaneous (be careful with this, can lock the simulation in a loop)
    :param element_name: (optional) name of the element
    :return: the resulting system and the message associated with its failure if requested
    """
    system = PetriNetSystem()

    working = Place(f"{element_name} {index} working", starting_marking=1)
    system.add_place(working)
    failed = Place(f"{element_name} {index} failed")
    system.add_system_fail_place(failed)

    failure = InstantTransition(f"{element_name} {index} failure") \
        if instantaneous else SlowTransition(f"{element_name} {index} failure", failure_rate)
    system.add_transition(failure)
    failure.add_upstream(working)
    failure.add_downstream(failed)

    failure_message: Message = None
    if fail_message:
        failure_message = Message(f"{element_name} {index} failed")
        failure.attach_emitter(failure_message, True)

    if reliability:
        return system, failure_message

    repair = InstantTransition(f"{element_name} {index} repair") \
        if instantaneous else SlowTransition(f"{element_name} {index} repair", repair_rate)
    system.add_transition(repair)
    repair.add_upstream(failed)
    repair.add_downstream(working)

    if fail_message:
        repair.attach_emitter(failure_message, False)

    return system, failure_message


def build_parallel_system(failure_rates, repair_rates, reliability=False, fail_message=False):
    if len(failure_rates) != len(repair_rates):
        raise ValueError("Failure and repair rates must have the same length")

    system, total_failure_message = build_1comp_petri(0, instantaneous=True,
                                                      element_name="system",
                                                      fail_message=fail_message,
                                                      reliability=True)
    working_system_state = system.places[0]
    failed_system_state = system.places[1]
    total_failure_transition = system.transitions[0]

    for i in range(len(failure_rates)):
        comp_system, comp_failure_message = build_1comp_petri(i, failure_rate=failure_rates[i],
                                                              repair_rate=repair_rates[i],
                                                              fail_message=True)
        system.merge(comp_system)

        total_failure_transition.attach_message(comp_failure_message, True)
        if not reliability:
            comeback_transition = InstantTransition(f"comeback due to repair {i}")
            comeback_transition.attach_message(comp_failure_message, False)
            comeback_transition.add_upstream(failed_system_state)
            comeback_transition.add_downstream(working_system_state)
            system.add_transition(comeback_transition)

    return system, total_failure_message


def acquire_characteristics():
    """
    function to test the algorithm
    """
    system, _ = build_parallel_system([1.0], [1.0], reliability=True)
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
        system, _ = build_parallel_system(rates, rates, reliability=False)
        start = time.perf_counter()
        print(1 - system.run_simulation(10, 10000))
        elapsed.append(time.perf_counter() - start)

    plt.plot(range(rates_amount), elapsed)
    plt.show()


t_performance()
