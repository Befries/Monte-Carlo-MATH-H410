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
        puts all the InstantTransition are at the start of the list, so they are checked first
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
            # life cycle of the net
            pass
