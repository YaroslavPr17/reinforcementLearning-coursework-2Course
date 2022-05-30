from Environment.model.utils import lane_status
from collections import namedtuple


class TransitionState:
    def __init__(self,
                 current_direction: str,
                 approximate_direction: str,
                 forward_available: bool,
                 left_available: bool,
                 right_available: bool,
                 lane_type: namedtuple('LaneInfo', 'is_left is_right'),
                 # is_on_road: bool,
                 # is_towards_intersection: bool,
                 ):
        self.current_direction = current_direction
        self.approximate_direction = approximate_direction
        self.forward_available = forward_available
        self.left_available = left_available
        self.right_available = right_available
        self.lane_type = lane_type


    def __eq__(self, other):
        return self.current_direction == other.current_direction and \
            self.approximate_direction == other.approximate_direction and \
            self.forward_available == other.forward_available and \
            self.left_available == other.left_available and \
            self.right_available == other.right_available and \
            self.lane_type == other.lane_type

    def __hash__(self):
        return hash((self.current_direction, self.approximate_direction, self.forward_available,
                     self.left_available, self.right_available, self.lane_type))

    def __str__(self):
        return f"{self.current_direction}\n" \
               f"{self.approximate_direction}\n" \
               f"{self.forward_available}\n" \
               f"{self.left_available}\n" \
               f"{self.right_available}\n" \
               f"{self.lane_type}\n\n"

    def __repr__(self):
        return self.__str__()


