from collections import namedtuple

from Environment.objects.model_object import Object
from Environment.model.utils import *

n_lanes = namedtuple('LanesNumber', ['N', 'W', 'E', 'S'])


class Lane:
    def __init__(self):
        pass

    def __str__(self):
        return '_'

    def __repr__(self):
        return self.__str__()


class Road(Object):
    """
    A class for Road cell

    Attributes
    ----------
    :param orientation: str
        The orientation of the road.
            'v' - vertical
            'h' - horizontal
    :param lanes: dict
        Dict for 2 of 4 directions to map on number of lanes.
            {'S': int, 'W': int} for horizontal road.
    :param hard_marking: str, default: 's'
        The type of the line which divides 2 road directions.
            'ds' - double solid
            's'  - single solid
            'b'  - broken
    :param soft_marking: str, default: 'b'
        The type of the line which divides lanes in the particular direction.
            'ds' - double solid
            's'  - single solid
            'b'  - broken
    """

    def __init__(self, orientation: str, lanes: dict, hard_marking: str = 's', soft_marking: str = 'b', num_lanes: n_lanes = None):
        super().__init__()
        self.label = 'R'
        self.orientation = orientation
        if self.orientation == 'v':
            self.lanes = {'N': [_ for _ in range(lanes['N'])][::-1],
                          'S': [_ for _ in range(lanes['S'])]}
        else:
            self.lanes = {'W': [_ for _ in range(lanes['W'])],
                          'E': [_ for _ in range(lanes['E'])][::-1]}

        if num_lanes is None:
            self.n_lanes = n_lanes(lanes.get('N', 0), lanes.get('W', 0), lanes.get('E', 0), lanes.get('S', 0))
        else:
            self.n_lanes = num_lanes
        self.n_lanes = self.n_lanes._asdict()

        self.hard_marking = hard_marking
        self.soft_marking = soft_marking

    def __str__(self):
        out = f"{self.label}" \
              f"({self.orientation}"
        if self.orientation == 'v':
            out += f"{self.lanes['S']}{'|'}{self.lanes['N']}"
            # out += '_' * len(self.lanes['S']) + '|' + '_' * len(self.lanes['N'])
        else:
            out += f"{self.lanes['W']}{'|'}{self.lanes['E']}"
            # out += '_' * len(self.lanes['W']) + '|' + '_' * len(self.lanes['E'])
        out += f"{self.hard_marking}" \
               f"{self.soft_marking})"

        return out.center(Road.slots)

    def __repr__(self):
        return self.__str__()

    def swap_directions(self):
        new_orientation = self.orientation

        if new_orientation == 'v':
            new_lanes: dict[str, int] = {'N': len(self.lanes['S']), 'S': len(self.lanes['N'])}
            new_n_lanes = n_lanes(new_lanes.get('S', 0), new_lanes.get('W', 0), new_lanes.get('E', 0),
                                  new_lanes.get('N', 0))
        else:
            new_lanes = {'W': len(self.lanes['E']), 'E': len(self.lanes['W'])}
            new_n_lanes = n_lanes(new_lanes.get('N', 0), new_lanes.get('E', 0), new_lanes.get('W', 0),
                                  new_lanes.get('S', 0))

        new_hard_marking = self.hard_marking

        new_soft_marking = self.soft_marking

        return Road(new_orientation, new_lanes, new_hard_marking, new_soft_marking, new_n_lanes)

    def __copy__(self):
        return Road(self.orientation, self.lanes, self.hard_marking, self.soft_marking)

    def is_lane_valid(self, direction: str, lane_num: int):
        if self.n_lanes.get(direction) is None:
            return False

        if lane_num is None or 0 <= lane_num <= self.n_lanes.get(direction) - 1:
            return True








