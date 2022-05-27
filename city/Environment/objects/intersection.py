from Environment.objects.model_object import Object
from collections import namedtuple

n_lanes = namedtuple('LanesNumber', ['N', 'W', 'E', 'S'])


class Intersection(Object):
    def __init__(self, lanes=None):
        super().__init__()
        if lanes is None:
            lanes = dict()
        self.label = 'X'
        self.n_lanes = n_lanes(lanes.get('N', 0), lanes.get('W', 0), lanes.get('E', 0), lanes.get('S', 0))._asdict()


    def __str__(self):
        return f"{self.label}" \
               f"({self.n_lanes.get('N', '')}{self.n_lanes.get('W', '')}{self.n_lanes.get('E', '')}{self.n_lanes.get('S', '')},"\
               f"{sum(self.n_lanes.values())})".center(Intersection.slots)

    def __repr__(self):
        return self.__str__()

    def __copy__(self):
        Intersection(self.n_lanes)
