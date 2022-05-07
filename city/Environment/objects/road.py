from Environment.objects.model_object import Object


class Road(Object):
    """
    A class for Road cell

    Attributes
    ----------
    :param orientation:  str
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

    def __init__(self, orientation: str, lanes: dict, hard_marking: str = 's', soft_marking: str = 'b'):
        self.label = 'R'
        self.direction = orientation
        self.lanes = lanes
        self.hard_marking = hard_marking
        self.soft_marking = soft_marking

    def __str__(self):
        if self.direction == 'v':
            return f"{self.label}({self.direction}{[self.lanes['S'], self.lanes['N']]}{self.hard_marking}" \
                   f"{self.soft_marking})".center(Road.slots)

        return f"{self.label}({self.direction}{[self.lanes['W'], self.lanes['E']]}{self.hard_marking}" \
               f"{self.soft_marking})".center(Road.slots)
