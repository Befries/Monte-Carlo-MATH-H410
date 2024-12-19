import random
from math import log


class Message:
    def __init__(self, name: str):
        self.name = name
        self.value = False

        # data collectors
        self.amount_of_broadcast = 0.0
        self.mean_amount_of_broadcast = 0.0
        self.amount_of_broadcast_variance = 0.0
        self.time_on = 0.0
        self.mean_time_on = 0.0
        self.time_on_variance = 0.0

    def clean_data(self):
        self.mean_amount_of_broadcast = 0.0
        self.amount_of_broadcast_variance = 0.0
        self.mean_time_on = 0.0
        self.time_on_variance = 0.0

    def broadcast(self, value):
        """
        sets the message value, increments the data collector counter
        """
        self.value = value
        self.amount_of_broadcast += 1

    def reset(self):
        self.value = False
        self.time_on = 0.0
        self.amount_of_broadcast = 0.0

    def update_time_on(self, time_passed):
        if self.value:
            self.time_on += time_passed

    def add_experience(self):
        if self.amount_of_broadcast == 0:
            return
        self.time_on /= (self.amount_of_broadcast + 1) // 2
        self.mean_time_on += self.time_on
        self.time_on_variance += self.time_on ** 2
        self.mean_amount_of_broadcast += self.amount_of_broadcast
        self.amount_of_broadcast_variance += self.amount_of_broadcast ** 2

    def treat_data(self, sample_size):
        self.mean_time_on /= sample_size
        self.mean_amount_of_broadcast /= sample_size
        self.time_on_variance = self.time_on_variance / sample_size - self.mean_time_on ** 2
        self.amount_of_broadcast_variance = (self.amount_of_broadcast_variance / sample_size -
                                             self.mean_amount_of_broadcast ** 2)


class Place:

    def __init__(self, name, starting_marking=0):
        self.name = name
        self.starting_marking = starting_marking
        self.token = starting_marking

        # data collectors
        self.sojourn_time = 0.0
        self.mean_total_sojourn_time = 0.0
        self.mean_sojourn_time = 0.0
        self.sojourn_time_variance = 0.0
        self.amount_of_entering = 0.0
        self.was_outside = True

    def clean_data(self):
        self.mean_sojourn_time = 0.0
        self.sojourn_time_variance = 0.0
        self.amount_of_entering = 0.0

    def reset_tokens(self):
        """
        sets content of the place to its initial amount of tokens
        """
        self.token = self.starting_marking
        self.sojourn_time = 0.0
        self.amount_of_entering = 0.0
        self.was_outside = True

    def update_time_on(self, time_passed: float):
        if self.token > 0:
            if self.was_outside:
                self.amount_of_entering += 1
                self.was_outside = False
            self.sojourn_time += time_passed
        else:
            self.was_outside = True

    def add_experience(self):
        if self.sojourn_time != 0.0:
            self.mean_total_sojourn_time += self.sojourn_time
            self.sojourn_time /= self.amount_of_entering
            self.mean_sojourn_time += self.sojourn_time
            self.sojourn_time_variance += self.sojourn_time ** 2

    def treat_data(self, sample_size):
        self.mean_sojourn_time /= sample_size
        self.mean_total_sojourn_time /= sample_size
        self.sojourn_time_variance = self.sojourn_time_variance / sample_size - self.mean_sojourn_time ** 2


class Transition:

    def __init__(self, name: str):
        self.name = name

        self.upstream_places: list[tuple[Place, int]] = []  # list of upstream places with the weight of their arc
        self.downstream_places: list[tuple[Place, int]] = []  # list of downstream places with the weight of their arc
        self.inhibitors: list[tuple[Place, int]] = []  # list of places the inhibitors arc comes from and their weights

        self.observed_message: list[tuple[Message, bool]] = []  # list of message to listen to
        self.broadcast_messages: list[tuple[Message, bool]] = []  # list of message to change

        self.stochastic: list[float] = []  # list of probabilities to if stochastic transition

        # data collectors
        self.firing_amount = 0.0
        self.mean_firing_amount = 0.0
        self.firing_amount_variance = 0.0

    def clean_data(self):
        self.mean_firing_amount = 0.0
        self.firing_amount_variance = 0.0

    def add_upstream(self, upstream_place: Place, weight=1):
        self.upstream_places.append((upstream_place, weight))

    def add_downstream(self, downstream_place: Place, weight=1):
        if len(self.stochastic) > 0:
            raise Exception("Stochastic transition, cannot add simple sub-places")
        self.downstream_places.append((downstream_place, weight))

    def add_downstream_stochastic(self, downstream_place: Place, transition_probability: float, weight=1):
        if len(self.downstream_places) > len(self.stochastic):
            raise Exception("Deterministic transition, cannot add stochastic sub-places")
        self.downstream_places.append((downstream_place, weight))
        self.stochastic.append(transition_probability)

    def add_inhibitor(self, inhibitor_place: Place, weight=1):
        self.inhibitors.append((inhibitor_place, weight))

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
        for inhibitor_place, inhibitor_weight in self.inhibitors:
            if inhibitor_place.token >= inhibitor_weight:
                return False
        for upstream_place, upstream_weight in self.upstream_places:
            if upstream_place.token < upstream_weight:
                return False
        return True

    def sample_firing(self) -> float:
        pass  # overridden in child classes

    def pass_tokens(self):
        """
        Fires the transition, pass the tokens down and broadcast its messages
        """
        self.firing_amount += 1.0
        for message, broadcast_value in self.broadcast_messages:
            message.broadcast(broadcast_value)

        for upstream_place, upstream_weight in self.upstream_places:
            upstream_place.token -= upstream_weight

        if len(self.stochastic) > 0:
            stochastic_place = random.choices(self.downstream_places, weights=self.stochastic)
            stochastic_place[0].token += stochastic_place[1]
            return

        for down_stream_place, downstream_weight in self.downstream_places:
            down_stream_place.token += downstream_weight

    def add_experience(self):
        self.mean_firing_amount += self.firing_amount
        self.firing_amount_variance += self.firing_amount ** 2

    def treat_data(self, sample_size):
        self.mean_firing_amount /= sample_size
        self.firing_amount_variance = self.firing_amount_variance / sample_size - self.mean_firing_amount ** 2


class InstantTransition(Transition):
    def __init__(self, name: str):
        super().__init__(name)

    def sample_firing(self) -> float:
        """
        :return: fires instantly
        """
        return 0.0


class ProbabilityRateTransition(Transition):
    def __init__(self, name: str, transition_rate: float):
        super().__init__(name)
        self.transition_rate = transition_rate

    def sample_firing(self) -> float:
        """
        :return: the time after which the transition is fired
        """
        return -1.0 / self.transition_rate * log(random.random())


class SlowTransition(Transition):
    def __init__(self, name: str, waiting_time: float):
        super().__init__(name)
        self.waiting_time = waiting_time
        self.time_left = waiting_time
        self.armed = False

    def sample_firing(self) -> float:
        return self.time_left

    def wait(self, time_passed: float):
        if self.armed:
            self.time_left -= time_passed

    def check_armed_state(self):
        self.armed = super().check_armed_state()
        if not self.armed:
            self.time_left = self.waiting_time  # if transition not armed, timer stay at max
        return self.armed

    def reset_timer(self):
        self.time_left = self.waiting_time
