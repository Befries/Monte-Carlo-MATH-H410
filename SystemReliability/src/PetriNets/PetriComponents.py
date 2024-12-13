import random
import numpy as np


class Message:
    def __init__(self, name: str):
        self.name = name
        self.value = False


class Place:

    def __init__(self, name, starting_marking=0):
        self.name = name
        self.starting_marking = starting_marking
        self.token = starting_marking

    def reset_tokens(self):
        """
        sets content of the place to its initial amount of tokens
        """
        self.token = self.starting_marking


class Transition:

    def __init__(self, name: str):
        self.name = name
        self.upstream_places: list[Place] = []
        self.upstream_weights: list[int] = []

        self.downstream_places: list[Place] = []
        self.downstream_weights: list[int] = []

        self.inhibitors: list[Place] = []
        self.inhibitor_weights: list[int] = []

        self.observed_message: list[tuple[Message, bool]] = []  # list of message to listen to
        self.broadcast_messages: list[tuple[Message, bool]] = []  # list of message to change

        self.stochastic: list[float] = []

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
            if message is not expected_message:
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
        for message, broadcast in self.broadcast_messages:
            message.value = broadcast

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
