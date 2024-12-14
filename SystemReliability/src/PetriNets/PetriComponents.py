import random
import numpy as np


class Message:
    def __init__(self, name: str):
        self.name = name
        self.value = False

        # data collectors
        self.mean_amount_of_broadcast = 0.0
        self.mean_time_on = 0.0

    def clean_data(self):
        self.mean_amount_of_broadcast = 0.0
        self.mean_time_on = 0.0

    def broadcast(self, value):
        """
        sets the message value, increments the data collector counter
        """
        self.value = value
        self.mean_amount_of_broadcast += 1

    def update_time_on(self, time_passed):
        if self.value:
            self.mean_time_on += time_passed


class Place:

    def __init__(self, name, starting_marking=0):
        self.name = name
        self.starting_marking = starting_marking
        self.token = starting_marking

        # data collectors
        self.sojourn_time = 0.0
        self.mean_sojourn_time = 0.0
        self.amount_of_entering = 0.0
        self.was_outside = True

    def clean_data(self):
        self.mean_sojourn_time = 0.0
        self.amount_of_entering = 0.0

    def reset_tokens(self):
        """
        sets content of the place to its initial amount of tokens
        """
        self.token = self.starting_marking
        self.sojourn_time = 0.0
        self.was_outside = True

    def update_time_on(self, time_passed):
        if self.token > 0:
            if self.was_outside:
                self.amount_of_entering += 1
                self.was_outside = False
            self.sojourn_time += time_passed
        else:
            self.was_outside = True



class Transition:

    def __init__(self, name: str):
        self.name = name
        self.upstream_places: list[Place] = []  # list of upstream places
        self.upstream_weights: list[int] = []  # list of weights on the arcs from upstream places

        self.downstream_places: list[Place] = []  # list of downstream places
        self.downstream_weights: list[int] = []  # list of weights on the arc to downstream places

        self.inhibitors: list[Place] = []  # list of places the inhibitors arc comes from
        self.inhibitor_weights: list[int] = []  # list of the weights on inhibitors arcs

        self.observed_message: list[tuple[Message, bool]] = []  # list of message to listen to
        self.broadcast_messages: list[tuple[Message, bool]] = []  # list of message to change

        self.stochastic: list[float] = []  # list of probabilities to if stochastic transition

        # data collectors
        self.mean_firing_amount = 0.0

    def clean_data(self):
        self.mean_firing_amount = 0.0

    def add_upstream(self, upstream_place: Place, weight=1):
        self.upstream_places.append(upstream_place)
        self.upstream_weights.append(weight)

    def add_downstream(self, downstream_place: Place, weight=1):
        if len(self.stochastic) > 0:
            raise Exception("Stochastic transition, cannot add simple sub-places")
        self.downstream_places.append(downstream_place)
        self.downstream_weights.append(weight)

    def add_downstream_stochastic(self, downstream_place: Place, transition_probability: float, weight=1):
        if len(self.downstream_places) > len(self.stochastic):
            raise Exception("Deterministic transition, cannot add stochastic sub-places")
        self.downstream_places.append(downstream_place)
        self.downstream_weights.append(weight)
        self.stochastic.append(transition_probability)

    def add_inhibitor(self, inhibitor_place: Place, weight=1):
        self.inhibitors.append(inhibitor_place)
        self.inhibitor_weights.append(weight)

    def attach_message(self, message: Message, expected_value: bool):
        self.observed_message.append((message, expected_value))

    def attach_emitter(self, message: Message, value: bool):
        self.broadcast_messages.append((message, value))

    def check_armed_state(self):
        """
        checks if all messages are True, inhibitors inactivated and that upstream places contain enough tokens
        :return: whether the transition is armed and can be traversed
        """
        for message, expected_message in self.observed_message:
            if message.value is not expected_message:
                return False
        for inhibitor_place, inhibitor_weight in zip(self.inhibitors, self.inhibitor_weights):
            if inhibitor_place.token >= inhibitor_weight:
                return False
        for upstream_place, upstream_weight in zip(self.upstream_places, self.upstream_weights):
            if upstream_place.token < upstream_weight:
                return False
        return True

    def sample_firing(self) -> float:
        pass  # overridden in child classes

    def pass_tokens(self):
        """
        Fires the transition, pass the tokens down and broadcast its messages
        """
        self.mean_firing_amount += 1.0
        for message, broadcast_value in self.broadcast_messages:
            message.broadcast(broadcast_value)

        for upstream_place, upstream_weight in zip(self.upstream_places, self.upstream_weights):
            upstream_place.token -= upstream_weight

        if len(self.stochastic) > 0:
            random.choices(list(zip(self.downstream_places, self.downstream_weights)), weights=self.stochastic)
            return

        for down_stream_place, downstream_weight in zip(self.downstream_places, self.downstream_weights):
            down_stream_place.token += downstream_weight


class InstantTransition(Transition):
    def __init__(self, name: str):
        super().__init__(name)

    def sample_firing(self) -> float:
        """
        :return: fires instantly
        """
        return 0.0


class SlowTransition(Transition):
    def __init__(self, name: str, transition_rate: float):
        super().__init__(name)
        self.transition_rate = transition_rate

    def sample_firing(self) -> float:
        """
        :return: the time after which the transition is fired
        """
        return -1.0/self.transition_rate * np.log(np.random.uniform())
