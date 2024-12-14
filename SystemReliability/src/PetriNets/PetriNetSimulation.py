from PetriComponents import *


class PetriNetSystem:

    def __init__(self):
        self.places: list[Place] = []  # all the places in the system
        self.transitions: list[Transition] = []  # all the transitions in the system
        self.messages: list[Message] = []  # all the messages in the system
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

    def merge(self, other: "PetriNetSystem"):
        """
        merge the other petri net with this one to form one system. The total fail place is the fail place of this
        system.
        :param other: another petri net
        """
        for place in other.places:
            self.add_place(place)
        for transition in other.transitions:
            self.add_transition(transition)

    def __cook__(self):
        """
        Puts all the InstantTransition at the start of the list, so they are checked first.
        Register all the messages in the net
        """
        self.transitions.sort(key=lambda a: type(a) is not InstantTransition)
        self.messages = []
        for transition in self.transitions:
            for message, _ in transition.broadcast_messages:
                if message not in self.messages:
                    self.messages.append(message)

    def clean_data_collectors(self):
        for place in self.places:
            place.clean_data()
        for transition in self.transitions:
            transition.clean_data()
        for message in self.messages:
            message.clean_data()

    def __treat_data_collector__(self, sample_size):
        for transition in self.transitions:
            transition.mean_firing_amount /= sample_size
        for place in self.places:
            place.mean_sojourn_time /= sample_size
            place.sojourn_time /= sample_size
        for message in self.messages:
            message.mean_time_on /= sample_size
            message.mean_amount_of_broadcast /= sample_size

    def run_simulation(self, duration, sample_size):
        """
        run a simulation of a given time over a sample of given size
        :param duration: the length of the simulation
        :param sample_size: the amount of token life to simulate
        :return: the reliability / availability (depends on the petri net)
        """
        self.__cook__()
        self.clean_data_collectors()

        fail_count = 0.0  # total number of system failed at duration
        for i in range(sample_size):
            self.simulate_tokens(duration)
            fail_count += 1 if self.system_fail_place.token > 0 else 0

        self.__treat_data_collector__(sample_size)
        return fail_count / sample_size  # return the reliability / availability depending on the petri net

    def simulate_tokens(self, duration):
        # reset the net
        for place in self.places:
            place.reset_tokens()
        for message in self.messages:
            message.value = False

        lifetime = 0.0
        # should update this condition -> if all transitions unarmed -> impossible to continue, therefore end of journey
        while lifetime < duration:
            fired_transition, time_passed = self.choose_candidate(duration, lifetime)

            lifetime += time_passed
            for place in self.places:
                place.update_time_on(time_passed)
            for message in self.messages:
                message.update_time_on(time_passed)

            if fired_transition is None:  # time exceeded or complete fail state
                break

            fired_transition.pass_tokens()
            # life cycle of the net
        for place in self.places:
            if place.sojourn_time != 0.0:
                place.mean_sojourn_time += place.sojourn_time / place.amount_of_entering

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
