from PetriComponents import *


class PetriNetSystem:

    def __init__(self):
        self.places: list[Place] = []  # all the places in the system
        self.transitions: list[Transition] = []  # all the transitions in the system
        self.system_fail_place: Place = None  # the place that causes the system to fail

    def add_place(self, place: Place):
        self.places.append(place)

    def add_system_fail_place(self, place: Place):
        if self.system_fail_place is not None:
            raise Exception("The petri net already contains a total fail place")
        self.add_place(place)
        self.system_fail_place = place

    def add_transition(self, transition: Transition):
        self.transitions.append(transition)

    def __sort__(self):
        """
        puts all the InstantTransition at the start of the list, so they are checked first
        """
        self.transitions.sort(key=lambda a: type(a) is not InstantTransition)

    def run_simulation(self, duration, sample_size):
        """
        run a simulation of a given time over a sample of given size
        :param duration: the length of the simulation
        :param sample_size: the amount of token life to simulate
        :return: the reliability / availability (depends on the petri net)
        """
        self.__sort__()
        fail_count = 0.0  # total number of system failed at duration
        for i in range(sample_size):
            self.simulate_tokens(duration)
            fail_count += 1 if self.system_fail_place.token > 0 else 0
            # scrap information contained in the different objects
        return fail_count / sample_size  # return the reliability / availability depending on the petri net

    def simulate_tokens(self, duration):
        for place in self.places:
            place.reset_tokens()

        lifetime = 0.0
        # should update this condition -> if all transitions unarmed -> impossible to continue, therefore end of journey
        while lifetime < duration:
            fired_transition, time_passed = self.choose_candidate(duration, lifetime)
            lifetime += time_passed
            if fired_transition is None:  # time exceeded or complete fail state
                # add info based on end situation
                break

            fired_transition.pass_tokens()
            # life cycle of the net

    def choose_candidate(self, duration, lifetime) -> tuple[Transition, float]:
        candidate = None
        candidate_transition_time = duration - lifetime  # max transition time in the time limit

        for transition in self.transitions:
            if transition.check_armed_state():
                candidate_time = transition.sample_firing()
                if candidate_time == 0.0:  # instant transition
                    return transition, 0.0
                if candidate_time < candidate_transition_time:
                    candidate_transition_time = candidate_time
                    candidate = transition

        return candidate, candidate_transition_time
