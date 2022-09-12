from Environment.model.utils import lane_status
from collections import namedtuple


class TransitionState:
    """
    The class describes transition state to generalize all possible general states for other maps.

    Parameters
    ----------
    current_direction: str,
        The capital letter, corresponding to one of cardinal directions.
            - 'N' - North
            - 'S' - South
            - 'W' - West
            - 'E' - East

    approximate_direction: str,
        One of 8 possible directions to define the approximate direction of Agent's destination point.
            'N', 'W', 'E', 'S', 'NE', 'NW', 'SE', 'SW'

    forward_available: bool,
        The flag describing whether moving forward is possible.

    left_available: bool,
        The flag describing whether turning left is possible.

    right_available: bool,
        The flag describing whether turning right is possible.

    lane_type: LaneInfo,
        The object which determines the type of lane, which Agent is standing on.
    """

    def __init__(self,
                 current_direction: str,
                 approximate_direction: str,
                 forward_available: bool,
                 left_available: bool,
                 right_available: bool,
                 lane_type: namedtuple('LaneInfo', 'is_left is_right'),
                 no_lane_towards: bool
                 ):
        self.current_direction = current_direction
        self.approximate_direction = approximate_direction
        self.forward_available = forward_available
        self.left_available = left_available
        self.right_available = right_available
        self.lane_type = lane_type
        self.no_lane_towards = no_lane_towards

    def __eq__(self, other):
        return self.current_direction == other.current_direction and \
            self.approximate_direction == other.approximate_direction and \
            self.forward_available == other.forward_available and \
            self.left_available == other.left_available and \
            self.right_available == other.right_available and \
            self.lane_type == other.lane_type and \
            self.no_lane_towards == other.no_lane_towards

    def __hash__(self):
        return hash((self.current_direction, self.approximate_direction, self.forward_available,
                     self.left_available, self.right_available, self.lane_type, self.no_lane_towards))

    def __str__(self):
        return f"{self.current_direction}\n" \
               f"{self.approximate_direction}\n" \
               f"{self.forward_available}\n" \
               f"{self.left_available}\n" \
               f"{self.right_available}\n" \
               f"{self.lane_type}\n" \
               f"{self.no_lane_towards}\n\n"

    def __repr__(self):
        return self.__str__()


