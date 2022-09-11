import numpy as np

from Environment.objects.model_object import Object
from Environment.model.utils import IntersectCoord
from collections import namedtuple

n_lanes = namedtuple('LanesNumber', ['N', 'W', 'E', 'S'])


class Intersection(Object):
    """
    A class for Road cell

    Attributes
    ----------
    :param lanes: dict
        Numbers of lanes in 4 geographical directions.
    """

    def __init__(self, lanes=None):
        super().__init__()
        if lanes is None:
            lanes = dict()
        self.label = 'X'
        self.n_lanes = n_lanes(lanes.get('N', 0), lanes.get('W', 0), lanes.get('E', 0), lanes.get('S', 0))._asdict()
        self.n_in_lanes = n_lanes(0, 0, 0, 0)._asdict()
        self.multi_lane_cls = dict()

    def __str__(self):
        return f"{self.label}" \
               f"({self.n_lanes.get('N', '')}{self.n_lanes.get('W', '')}{self.n_lanes.get('E', '')}{self.n_lanes.get('S', '')},"\
               f"{sum(self.n_lanes.values())})".ljust(Intersection.slots)

    def __repr__(self):
        return self.__str__()
