from PetriComponents import *

class PetriNetSystem:

    places: list[Place]
    transitions: list[Transition]

    def __init__(self):
        pass

    def add_place(self, place):
        self.places.append(place)

    def add_transition(self, transition):
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
        :return:
        """
        self.__sort__()
        for i in range(sample_size):
            self.simulate_tokens(duration)

    def simulate_tokens(self, duration):
        for place in self.places:
            place.reset_tokens()

        lifetime = 0.0
        # should update this condition -> if all transitions unarmed -> impossible to continue, therefore end of journey
        while lifetime < duration:
            transition_fired, time_passed = self.choose_candidate(duration, lifetime)
            lifetime += time_passed
            if transition_fired is None:  # time exceeded or complete fail state
                # add info based on end situation
                break

            transition_fired.pass_tokens()
            # life cycle of the net

    def choose_candidate(self, duration, lifetime) -> tuple[Transition, float]:
        candidate = None
        candidate_transition_time = duration - lifetime  # max transition time
        for transition in self.transitions:
            if transition.check_armed_state():
                candidate_time = transition.sample_firing()
                if candidate_time is 0.0:  # instant transition
                    return transition, 0.0
                if candidate_time < candidate_transition_time:
                    candidate_transition_time = candidate_time
                    candidate = transition
        return candidate, candidate_transition_time
