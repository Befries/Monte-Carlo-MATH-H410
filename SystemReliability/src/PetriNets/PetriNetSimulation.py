from PetriComponents import *


class PetriNetSystem:

    def __init__(self):
        self.places: list[Place] = []  # all the places in the system
        self.transitions: list[Transition] = []  # all the transitions in the system
        self.messages: list[Message] = []  # all the messages in the system
        self.system_fail_place: Place = None  # the place that causes the system to fail
        self.slow_transitions: list[SlowTransition] = []  # keep a list of slow transitions to make them wait separately

    def add_place(self, place: Place):
        self.places.append(place)

    def add_system_fail_place(self, place: Place):
        if self.system_fail_place is not None:
            raise Exception("The petri net already contains a total fail place")
        self.add_place(place)
        self.system_fail_place = place

    def add_transition(self, transition: Transition):
        self.transitions.append(transition)

    def __cook__(self):
        """
        Prepare the system before a simulation
        Puts all the InstantTransition at the start of the list, so they are checked first.
        Register all the messages in the net.
        distinguish all slow transitions to make them wait
        """
        self.transitions.sort(key=lambda a: type(a) is not InstantTransition)
        self.messages = []
        for transition in self.transitions:
            for message, _ in transition.broadcast_messages:
                if message not in self.messages:
                    self.messages.append(message)
        for transition in self.transitions:
            if type(transition) is SlowTransition:
                self.slow_transitions.append(transition)

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
            place.treat_data(sample_size)
        for message in self.messages:
            message.treat_data(sample_size)

    def run_simulation(self, duration, sample_size) -> tuple[float, float]:
        """
        run a simulation of a given time over a sample of given size
        :param duration: the length of the simulation
        :param sample_size: the amount of token life to simulate
        :return: the reliability / availability (depends on the petri net)
        """
        self.__cook__()
        self.clean_data_collectors()

        fail_count = 0.0  # total number of system failed at duration
        var_count = 0.0  # total number of
        for i in range(sample_size):
            self.simulate_tokens(duration)
            fail_count += self.system_fail_place.token
            var_count += self.system_fail_place.token * self.system_fail_place.token

        self.__treat_data_collector__(sample_size)
        estimation = fail_count / sample_size
        return estimation, var_count / sample_size - estimation ** 2

    def simulate_tokens(self, duration):
        # reset the net
        for place in self.places:
            place.reset_tokens()
        for message in self.messages:
            message.reset()
        for slow_transition in self.slow_transitions:
            slow_transition.reset_timer()

        lifetime = 0.0
        # should update this condition -> if all transitions unarmed -> impossible to continue, therefore end of journey
        while lifetime < duration:
            fired_transition, time_passed = self.choose_candidate(duration, lifetime)

            lifetime += time_passed
            for slow_transition in self.slow_transitions:
                slow_transition.wait(time_passed)
            for place in self.places:
                place.update_time_on(time_passed)
            for message in self.messages:
                message.update_time_on(time_passed)

            if fired_transition is None:  # time exceeded or complete fail state
                break

            fired_transition.pass_tokens()
            # life cycle of the net
        for place in self.places:
            place.add_experience()
        for message in self.messages:
            message.add_experience()
        for transition in self.transitions:
            transition.add_experience()

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
