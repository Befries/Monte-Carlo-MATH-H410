
class Message:
    def __init__(self, name: str):
        self.name = name
        self.activated = False


class Place:
    token: int

    def __init__(self, name, starting_marking=0):
        self.name = name
        self.starting_marking = starting_marking

    def reset_tokens(self):
        """
        sets content of the place to its initial amount of tokens
        """
        self.token = self.starting_marking


class Transition:
    upstream_places: list[Place]
    upstream_weights: list[int]

    downstream_places: list[Place]
    downstream_weights: list[int]

    inhibitors: list[Place]
    inhibitor_weights: list[int]

    received_messages: list[Message]
    sent_messages: list[Message]

    def __init__(self, name: str):
        self.name = name

    def add_upstream(self, upstream_place: Place, weight=1):
        self.upstream_places.append(upstream_place)
        self.upstream_weights.append(weight)

    def add_downstream(self, downstream_place: Place, weight=1):
        self.downstream_places.append(downstream_place)
        self.downstream_weights.append(weight)

    def add_inhibitor(self, inhibitor_place: Place, weight=1):
        self.inhibitors.append(inhibitor_place)
        self.inhibitor_weights.append(weight)

    def check_armed_state(self):
        """
        checks if all messages are True, inhibitors inactivated and that upstream places contain enough tokens
        :return: whether the transition is armed and can be traversed
        """
        for message in self.received_messages:
            if not message:
                return False
        for inhibitor_place, inhibitor_weight in zip(self.inhibitors, self.inhibitor_weights):
            if inhibitor_place.token >= inhibitor_weight:
                return False
        for upstream_place, upstream_weight in zip(self.upstream_places, self.upstream_weights):
            if upstream_place.token < upstream_weight:
                return False
        return True


class InstantTransition(Transition):
    def __init__(self, name: str):
        super().__init__(name)


class SlowTransition(Transition):
    def __init__(self, name: str, transition_rate: float):
        super().__init__(name)
        self.transition_rate = transition_rate
