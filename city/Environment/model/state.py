import math
from collections import namedtuple
from typing import Union
import numpy as np
from pprint import pprint

from deprecated.classic import deprecated

from Environment.model import constants
from Environment.model.utils import *
from Environment.objects import ground, road, intersection
from Environment import city
from Environment.model.utils import *
from Environment.model.constants import *
from Environment.objects import *


def lane_status(is_left: bool, is_right: bool):
    return namedtuple('LaneInfo', ('is_left', 'is_right'))(is_left, is_right)

def closest(target_dir: str, dirs: list):
    directions = constants.cardinal_directions
    distances = []
    for d in dirs:
        dist = abs(directions.index(target_dir) - directions.index(d))
        dist %= 5
        distances.append(dist)
    res = list(zip(dirs, distances))
    res = filter(lambda t: t[1] <= 1, res)
    res = [t[0] for t in res]
    return res


class State:
    """
    The class describes an Observation (in terms of RL), which means several fields which determine the position of Agent
    within our Environment.

    Attributes
    ----------
    :param city_model: The Environment which Agent interacts with
    :type city_model: list[list]
    :param current_direction: The capital letter, corresponding to one of cardinal directions.
        'N' - North
        'S' - South
        'W' - West
        'E' - East
    :type current_direction: str
    :param car_coordinates: The collections.namedtuple formatted to represent Agent's current coordinates (similar with numpy-array's.).
        axis0 - vertical coordinate
        axis1 - horizontal coordinate
    :type car_coordinates: CarCoord
    :param destination_coordinates: The collections.namedtuple formatted to represent coordinates of destination point (similar with numpy-array's.).
        axis0 - vertical coordinate
        axis1 - horizontal coordinate
    :type destination_coordinates: DestCoord
    :param current_lane: The ordinal number of the current lane taken by Agent.
        None - if the lane cannot be defined
        int - if Agent is on road or ready to start from the intersection.
    :type: current_lane: int or None
    :param observation: the pool of cell of Environment, witnessing by Agent.
    :type: observation: np.ndarray

    """

    def __init__(self, city_model: list,
                 current_direction: str,
                 car_coordinates: CarCoord,
                 destination_coordinates: DestCoord,
                 current_lane: Union[int, None],
                 observation: np.ndarray):
        self.city_model = city_model
        self.current_direction = current_direction
        self.car_coordinates = car_coordinates
        self.destination_coordinates = destination_coordinates
        self.current_lane = current_lane
        self.observation = observation

        self._car_pos = self.observation[1][1]
        self._in_front_of = self.observation[0][1]
        self._diag_left = self.observation[0][0]
        self._diag_right = self.observation[0][2]
        self._left = self.observation[1][0]
        self._right = self.observation[1][2]

    def __str__(self):
        return f"{self.current_direction = }\n" \
               f"{self.car_coordinates}\n" \
               f"{self.destination_coordinates}\n" \
               f"{self.current_lane = }\n" \
               f"{self.observation}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
       return self.current_direction == other.current_direction and self.current_lane == other.current_lane and \
                self.car_coordinates == other.car_coordinates and self.destination_coordinates == other.destination_coordinates

    def __hash__(self):
        return hash(('NWES'.index(self.current_direction), (self.car_coordinates.axis0, self.car_coordinates.axis1),
                     (self.destination_coordinates.axis0, self.destination_coordinates.axis1), self.current_lane))

    def _lane_type(self) -> lane_status:
        n_lanes: int = self.city_model[self.car_coordinates.axis0][self.car_coordinates.axis1]. \
            n_lanes.get(self.current_direction)
        if n_lanes == 1:
            return lane_status(True, True)
        elif n_lanes == 0:
            return None
        elif self.current_lane == 0:
            return lane_status(True, False)
        elif self.current_lane == n_lanes - 1:
            return lane_status(False, True)
        else:
            return lane_status(False, False)

    def _approx_direction(self):
        Vector = namedtuple('Vector', ('axis0', 'axis1'))
        vec = Vector(self.destination_coordinates.axis0 - self.car_coordinates.axis0,
                     self.destination_coordinates.axis1 - self.car_coordinates.axis1)

        if math.isclose(vec.axis1, 0.0):
            alpha = 90 if vec.axis0 >= 0 else 270
        elif math.isclose(vec.axis0, 0.0):
            alpha = 0 if vec.axis1 >= 0 else 180
        else:
            tg_alpha = vec.axis0 / vec.axis1
            print(f"{tg_alpha = }")

            alpha = math.degrees(math.atan(tg_alpha))

            if alpha < 0:
                alpha += 360
            if vec.axis0 < 0 and vec.axis1 < 0:
                alpha += 180
            if vec.axis0 > 0 and vec.axis1 < 0:
                alpha -= 180

        print(f"{alpha = }")
        for angle in np.arange(22.5, 292.6, 45):
            # print(angle)
            if angle <= alpha < angle + 45:
                approx_dir = constants.cardinal_directions[int(angle // 45)]
                break
        else:
            approx_dir = 'N'

        return approx_dir


    def forward(self):
        """
        :return: destination state after moving forward from the current state.
        :rtype: State
        """
        new_current_direction = self.current_direction
        if self.current_direction == 'W':
            new_car_coordinates = CarCoord(self.car_coordinates.axis0, self.car_coordinates.axis1 - 1)
        elif self.current_direction == 'E':
            new_car_coordinates = CarCoord(self.car_coordinates.axis0, self.car_coordinates.axis1 + 1)
        elif self.current_direction == 'N':
            new_car_coordinates = CarCoord(self.car_coordinates.axis0 - 1, self.car_coordinates.axis1)
        else:
            new_car_coordinates = CarCoord(self.car_coordinates.axis0 + 1, self.car_coordinates.axis1)

        new_destination_coordinates = self.destination_coordinates


        reward = rewards.basic_forward
        is_done = False
        if isinstance(self._in_front_of, ground.Ground):
            # * -> Ground
            # No way forward
            new_current_lane = None
            reward += constants.rewards.out_of_road
            is_done = True

        elif isinstance(self._in_front_of, intersection.Intersection):
            # * -> Intersection
            new_current_lane = self.current_lane


        elif isinstance(self._car_pos, intersection.Intersection):
            # Intersection -> Road
            if self.current_lane is not None:
                new_current_lane = self.current_lane
            elif self._in_front_of.n_lanes.get(new_current_direction) != 0:
                new_current_lane = np.random.randint(0, self._in_front_of.n_lanes.get(new_current_direction))
            else:
                new_current_lane = None
                reward += constants.rewards.solid_line_crossing
                is_done = True

        elif self._in_front_of.n_lanes.get(new_current_direction) == 0:
            # Road -> Road
            # No lanes forward, only single opposite direction
            new_current_lane = None
            reward += constants.rewards.out_of_road
            is_done = True

        elif isinstance(self._car_pos, road.Road) and \
                self._in_front_of.n_lanes.get(self.current_direction) < self._car_pos.n_lanes.get(self.current_direction) and \
                self.current_lane == self._car_pos.n_lanes.get(self.current_direction) - 1:
            # Road narrowing happened
            # If moving on the right lane, nothing happens. If on the left lane, car drives off the road.
            new_current_lane = None
            reward += constants.rewards.out_of_road
            is_done = True

        else:
            new_current_lane = self.current_lane


        if new_car_coordinates.axis0 == new_destination_coordinates.axis0 and \
                new_car_coordinates.axis1 == new_destination_coordinates.axis1:
            is_done = True
            reward += constants.rewards.reached_destination

            if new_current_lane != 0:
                reward += constants.rewards.stop_in_the_middle_road

        new_observation = city._observation(self.city_model, new_current_direction, new_car_coordinates, normalize=True)

        return State(self.city_model, new_current_direction, new_car_coordinates, new_destination_coordinates,
                     new_current_lane, new_observation), reward, is_done

    def left(self):
        """
        :return: destination state after turning left from the current state.
        :rtype: State
        """
        new_current_direction = left(self.current_direction)

        new_car_coordinates = self.car_coordinates

        new_destination_coordinates = self.destination_coordinates

        reward = rewards.basic_left_right
        is_done = False
        if isinstance(self._car_pos, road.Road):
            # Unexpected turn outside the intersection
            new_current_lane = None
            reward += constants.rewards.turn_on_road
            is_done = True

        elif isinstance(self._car_pos, intersection.Intersection):
            new_current_lane = self._car_pos.n_lanes.get(new_current_direction)
            if new_current_lane != 0:
                new_current_lane -= 1
            else:
                new_current_lane = None

            if self.current_lane is None:
                pass
            elif self.current_lane == self._car_pos.n_lanes.get(self.current_direction) - 1:
                reward += rewards.turn_from_the_appropriate_lane
            else:
                reward += rewards.wrong_lane_to_turn

        else:
            print("left. Unexpected position")

        new_observation = city._observation(self.city_model, new_current_direction, new_car_coordinates, normalize=True)

        return State(self.city_model, new_current_direction, new_car_coordinates, new_destination_coordinates,
                     new_current_lane, new_observation), reward, is_done

    def right(self):
        """
        :return: destination state after turning right from the current state.
        :rtype: State
        """
        new_current_direction = right(self.current_direction)

        new_car_coordinates = self.car_coordinates

        new_destination_coordinates = self.destination_coordinates

        reward = rewards.basic_left_right
        is_done = False
        if isinstance(self._car_pos, road.Road):
            # Unexpected turn outside the intersection
            new_current_lane = None
            reward += constants.rewards.turn_on_road
            is_done = True

        elif isinstance(self._car_pos, intersection.Intersection):
            new_current_lane = self._car_pos.n_lanes.get(new_current_direction)
            if new_current_lane != 0:
                new_current_lane = 0
            else:
                new_current_lane = None

            if self.current_lane is None:
                pass
            elif self.current_lane == 0:
                reward += rewards.turn_from_the_appropriate_lane
            else:
                reward += rewards.wrong_lane_to_turn
        else:
            print("right. Unexpected position")

        new_observation = city._observation(self.city_model, new_current_direction, new_car_coordinates, normalize=True)

        return State(self.city_model, new_current_direction, new_car_coordinates, new_destination_coordinates,
                     new_current_lane, new_observation), reward, is_done

    def turn_around(self):
        """
        :return: destination state after turning around from the current state.
        :rtype: State
        """
        new_current_direction = opposite(self.current_direction)

        new_car_coordinates = self.car_coordinates

        new_destination_coordinates = self.destination_coordinates

        reward = rewards.basic_turn_around
        is_done = False
        if isinstance(self._car_pos, intersection.Intersection):
            # When intersection, cannot define lane
            reward += constants.rewards.turn_around_on_intersection
            new_current_lane = None
        elif isinstance(self._car_pos, road.Road):
            # On road
            reward += rewards.turn_around_on_road
            if self.current_lane is None:
                pass
            elif self.current_lane != self._car_pos.n_lanes.get(self.current_direction) - 1:
                # Current lane is not left
                reward += rewards.wrong_lane_to_turn
            else:
                reward += rewards.turn_from_the_appropriate_lane

            if self._car_pos.hard_marking in ('ds', 's'):
                # Hard marking is solid or double solid
                reward += constants.rewards.turn_around_through_solid_line

            if self._car_pos.n_lanes.get(new_current_direction) == 0:
                # No opposite lanes available
                new_current_lane = None
                reward += constants.rewards.out_of_road
                is_done = True
            else:
                if self.current_lane is None:
                    new_current_lane = None
                else:
                    if new_current_direction in 'NE':
                        new_current_lane = self._car_pos.lanes.get(self.current_direction)\
                            [self._car_pos.n_lanes.get(new_current_direction) - 1]
                    else:
                        new_current_lane = self._car_pos.lanes.get(new_current_direction) \
                        [self._car_pos.n_lanes.get(new_current_direction) - 1]

        if new_car_coordinates.axis0 == new_destination_coordinates.axis0 and \
            new_car_coordinates.axis1 == new_destination_coordinates.axis1:
            is_done = True
            reward += constants.rewards.reached_destination

            if new_current_lane != 0:
                reward += constants.rewards.stop_in_the_middle_road



        new_observation = city._observation(self.city_model, new_current_direction, new_car_coordinates, normalize=True)

        return State(self.city_model, new_current_direction, new_car_coordinates, new_destination_coordinates,
                     new_current_lane, new_observation), reward, is_done

    def left_lane(self):
        """
        :return: destination state after moving to the left lane from the current state.
        :rtype: State
        """
        new_current_direction = self.current_direction

        if self.current_direction == 'W':
            new_car_coordinates = CarCoord(self.car_coordinates.axis0, self.car_coordinates.axis1 - 1)
        elif self.current_direction == 'E':
            new_car_coordinates = CarCoord(self.car_coordinates.axis0, self.car_coordinates.axis1 + 1)
        elif self.current_direction == 'N':
            new_car_coordinates = CarCoord(self.car_coordinates.axis0 - 1, self.car_coordinates.axis1)
        else:
            new_car_coordinates = CarCoord(self.car_coordinates.axis0 + 1, self.car_coordinates.axis1)

        new_destination_coordinates = self.destination_coordinates

        reward = rewards.basic_change_lane
        is_done = False
        if isinstance(self._in_front_of, road.Road):
            # On road
            if self._in_front_of.is_lane_valid(new_current_direction, self.current_lane):
                # Current lane forward is available
                if self.current_lane is None or self._in_front_of.is_lane_valid(new_current_direction, self.current_lane + 1):
                    # Left lane forward is available
                    if self.current_lane is None:
                        new_current_lane = None
                    else:
                        new_current_lane = self.current_lane + 1
                else:
                    if self._in_front_of.n_lanes.get(opposite(self.current_direction)) > 0:
                        new_current_lane = None
                        reward = rewards.solid_line_crossing
                        is_done = True
                    else:
                        new_current_lane = None
                        reward = rewards.out_of_road
                        is_done = True
            else:
                new_current_lane = None
                reward = rewards.out_of_road
                is_done = True
        else:
            new_current_lane = None
            reward = rewards.change_lane_not_on_road
            is_done = True

        if new_car_coordinates.axis0 == new_destination_coordinates.axis0 and \
                new_car_coordinates.axis1 == new_destination_coordinates.axis1:
            is_done = True
            reward += constants.rewards.reached_destination

            if new_current_lane != 0:
                reward += constants.rewards.stop_in_the_middle_road

        new_observation = city._observation(self.city_model, new_current_direction, new_car_coordinates, normalize=True)

        return State(self.city_model, new_current_direction, new_car_coordinates, new_destination_coordinates,
                     new_current_lane, new_observation), reward, is_done

    def right_lane(self):
        """
        :return: destination state after moving to the right lane from the current state.
        :rtype: State
        """
        new_current_direction = self.current_direction

        if self.current_direction == 'W':
            new_car_coordinates = CarCoord(self.car_coordinates.axis0, self.car_coordinates.axis1 - 1)
        elif self.current_direction == 'E':
            new_car_coordinates = CarCoord(self.car_coordinates.axis0, self.car_coordinates.axis1 + 1)
        elif self.current_direction == 'N':
            new_car_coordinates = CarCoord(self.car_coordinates.axis0 - 1, self.car_coordinates.axis1)
        else:
            new_car_coordinates = CarCoord(self.car_coordinates.axis0 + 1, self.car_coordinates.axis1)

        new_destination_coordinates = self.destination_coordinates

        reward = rewards.basic_change_lane
        is_done = False
        if isinstance(self._in_front_of, road.Road):
            # Happens on road
            if self._in_front_of.is_lane_valid(new_current_direction, self.current_lane):
                # Current lane forward is available
                if self.current_lane is None or self._in_front_of.is_lane_valid(new_current_direction, self.current_lane - 1):
                    # Right lane forward is available
                    if self.current_lane is None:
                        new_current_lane = None
                    else:
                        new_current_lane = self.current_lane - 1
                else:
                    new_current_lane = None
                    reward = rewards.out_of_road
                    is_done = True
            else:
                new_current_lane = None
                reward = rewards.out_of_road
                is_done = True
        else:
            new_current_lane = None
            reward = rewards.change_lane_not_on_road
            is_done = True

        if new_car_coordinates.axis0 == new_destination_coordinates.axis0 and \
                new_car_coordinates.axis1 == new_destination_coordinates.axis1:
            is_done = True
            reward += constants.rewards.reached_destination

            if new_current_lane != 0:
                reward += constants.rewards.stop_in_the_middle_road

        new_observation = city._observation(self.city_model, new_current_direction, new_car_coordinates, normalize=True)

        return State(self.city_model, new_current_direction, new_car_coordinates, new_destination_coordinates,
                     new_current_lane, new_observation), reward, is_done

    @deprecated("Debug method. Use __str__ instead.")
    def visualize(self):
        out = f"{self.car_coordinates} -> {self.destination_coordinates}" \
               f"dir={self.current_direction}, lane={self.current_lane}"
        return out