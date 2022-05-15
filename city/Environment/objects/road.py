from Environment.objects.model_object import Object


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
        super().__init__()
        self.label = 'R'
        self.orientation = orientation
        if self.orientation == 'v':
            self.lanes = {'N': [Lane() for _ in range(lanes['N'])],
                          'S': [Lane() for _ in range(lanes['S'])]}
        else:
            self.lanes = {'W': [Lane() for _ in range(lanes['W'])],
                          'E': [Lane() for _ in range(lanes['E'])]}
        self.hard_marking = hard_marking
        self.soft_marking = soft_marking

    def __str__(self):
        out = f"{self.label}" \
              f"({self.orientation}"
        if self.orientation == 'v':
            out += '_' * len(self.lanes['S']) + '|' + '_' * len(self.lanes['N'])
        else:
            out += '_' * len(self.lanes['W']) + '|' + '_' * len(self.lanes['E'])
        out += f"{self.hard_marking}" \
               f"{self.soft_marking})"

        return out.center(Road.slots)

    def __repr__(self):
        return self.__str__()
