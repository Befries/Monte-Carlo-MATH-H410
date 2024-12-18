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
    place[0] = working
    place[1] = failed
    transition[0] = failure
    transition[1] = repair
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
        if instantaneous else ProbabilityRateTransition(f"{element_name} {index} failure", failure_rate)
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
        if instantaneous else ProbabilityRateTransition(f"{element_name} {index} repair", repair_rate)
    system.add_transition(repair)
    repair.add_upstream(failed)
    repair.add_downstream(working)

    if fail_message:
        repair.attach_emitter(failure_message, False)

    return system, failure_message


def build_parallel_system(failure_rates, repair_rates, reliability=False, fail_message=False):
    if len(failure_rates) != len(repair_rates):
        raise ValueError("Failure and repair rates must have the same length")

    if not reliability:
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

            comeback_transition = InstantTransition(f"comeback due to repair {i}")
            comeback_transition.attach_message(comp_failure_message, False)
            comeback_transition.add_upstream(failed_system_state)
            comeback_transition.add_downstream(working_system_state)
            system.add_transition(comeback_transition)
        return system, None

    system = PetriNetSystem()

    failed_system_state = Place("total failure", 0)
    total_failure_transition = InstantTransition("total system failure")
    total_failure_transition.add_downstream(failed_system_state)

    system.add_transition(total_failure_transition)
    system.add_system_fail_place(failed_system_state)

    if fail_message:
        total_failure_message = Message("total system failure")
        total_failure_transition.attach_emitter(total_failure_message, True)

    for i in range(len(failure_rates)):
        comp_system, _ = build_1comp_petri(i, failure_rates[i], repair_rate=repair_rates[i])
        system.merge(comp_system)
        total_failure_transition.add_upstream(comp_system.places[1])

    return system, None


def build_parallel_inhibitor(failure_rates, repair_rates, ):
    """
    just to test that the availability system can work with inhibitors
    """
    system, total_failure_message = build_1comp_petri(0, instantaneous=True,
                                                      element_name="system",
                                                      reliability=True)
    working_system_state = system.places[0]
    failed_system_state = system.places[1]
    total_failure_transition = system.transitions[0]

    for i in range(len(failure_rates)):
        comp_system, comp_failure_message = build_1comp_petri(i, failure_rate=failure_rates[i],
                                                              repair_rate=repair_rates[i])
        system.merge(comp_system)
        total_failure_transition.add_inhibitor(comp_system.places[0])

        comeback_transition = InstantTransition(f"comeback due to repair {i}")
        comeback_transition.add_inhibitor(comp_system.places[1])
        comeback_transition.add_upstream(failed_system_state)
        comeback_transition.add_downstream(working_system_state)
        system.add_transition(comeback_transition)
    return system


def build_two_comp_passive_redundancy_reliability(failure_rate1, failure_rate2, repair_rate1):
    system = PetriNetSystem()
    primary_system, f1_failure = build_1comp_petri(1, fail_message=True, failure_rate=failure_rate1,
                                                   repair_rate=repair_rate1)
    system.merge(primary_system)
    second_system, _ = build_1comp_petri(2, failure_rate=failure_rate2, reliability=True)
    system.merge(second_system)
    second_system.places[0].starting_marking = 0

    standby_place = Place("standby", 1)
    system.add_place(standby_place)

    start_standby_transition = InstantTransition("start standby unit")
    system.add_transition(start_standby_transition)
    start_standby_transition.add_upstream(standby_place)
    start_standby_transition.add_downstream(second_system.places[0])
    start_standby_transition.attach_message(f1_failure, True)

    return_to_standby_transition = InstantTransition("return to standby")
    system.add_transition(return_to_standby_transition)
    return_to_standby_transition.add_upstream(second_system.places[0])
    return_to_standby_transition.add_downstream(standby_place)
    return_to_standby_transition.attach_message(f1_failure, False)

    end_transition = InstantTransition("end")
    system.add_transition(end_transition)
    end_transition.add_upstream(primary_system.places[1])
    end_transition.add_upstream(second_system.places[1])

    end_place = Place("system failure")
    system.add_system_fail_place(end_place)
    end_transition.add_downstream(end_place)

    return system


def build_obsolescence_strategy_k_net(unit_amount, k, fail_rate_old, fail_rate_new, replacement_cost, corrective_cost,
                                      intervention_cost):
    system = PetriNetSystem()
    counter_place = Place("counter")
    system.add_place(counter_place)
    replaced_all_place = Place("replaced all")
    system.add_place(replaced_all_place)
    cost_place = Place("cost")
    system.add_system_fail_place(cost_place)  # to compute the average cost

    strategy_transition = InstantTransition("strategy transition")
    system.add_transition(strategy_transition)
    strategy_transition.add_upstream(counter_place, k)
    strategy_message = Message("strategy transition")
    strategy_transition.attach_emitter(strategy_message, True)

    def build_module(index):
        old_place = Place(f"old {index}", starting_marking=1)
        system.add_place(old_place)

        old_fail_transition = ProbabilityRateTransition(f"old fail {index}", fail_rate_old)
        system.add_transition(old_fail_transition)
        old_replace_transition = InstantTransition(f"old replace {index}")
        system.add_transition(old_replace_transition)
        old_replace_transition.attach_message(strategy_message, True)

        new_place = Place(f"new {index}")
        system.add_place(new_place)

        old_fail_transition.add_upstream(old_place)
        old_fail_transition.add_downstream(new_place)
        old_replace_transition.add_upstream(old_place)
        old_replace_transition.add_downstream(new_place)

        old_fail_transition.add_downstream(counter_place)
        old_fail_transition.add_downstream(cost_place, weight=(replacement_cost + intervention_cost))
        old_replace_transition.add_downstream(cost_place, weight=replacement_cost)

        fail_place = Place(f"fail {index}")
        system.add_place(fail_place)

        new_fail_transition = ProbabilityRateTransition(f"new fail {index}", fail_rate_new)
        system.add_transition(new_fail_transition)
        new_repair_transition = InstantTransition(f"new repair {index}")
        system.add_transition(new_repair_transition)

        new_fail_transition.add_upstream(new_place)
        new_fail_transition.add_downstream(fail_place)
        new_repair_transition.add_upstream(fail_place)
        new_repair_transition.add_downstream(new_place)

        new_fail_transition.add_downstream(cost_place, weight=(corrective_cost + intervention_cost))

    for i in range(unit_amount):
        build_module(i + 1)

    return system, cost_place
