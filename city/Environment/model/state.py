import math
from collections import namedtuple
from Environment.model import constants
from Environment.model.utils import *

import numpy as np


def lane_status(is_left: bool, is_right: bool):
    return namedtuple('LaneInfo', ('is_left', 'is_right'))(is_left, is_right)


class State:
    def __init__(self, city_model: list,
                 current_direction: str,
                 car_coordinates: CarCoord,
                 destination_coordinates: DestCoord,
                 current_lane: int,
                 observation: np.ndarray):
        self.city_model = city_model
        self.current_direction = current_direction
        self.car_coordinates = car_coordinates
        self.destination_coordinates = destination_coordinates
        self.current_lane = current_lane
        self.observation = observation

    def __str__(self):
        return f"{self.current_direction = }\n" \
               f"{self.car_coordinates}\n" \
               f"{self.destination_coordinates}\n" \
               f"{self.current_lane = }\n" \
               f"{self.observation}"

    def __repr__(self):
        return self.__str__()

    def to_learning_state(self):
        learning_state = ()
        Vector = namedtuple('Vector', ('axis0', 'axis1'))
        vec = Vector(self.destination_coordinates.axis0 - self.car_coordinates.axis0,
                     self.destination_coordinates.axis1 - self.car_coordinates.axis1)
        print(vec)

        # Approximate direction preprocessing
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
            print(angle)
            if angle <= alpha < angle + 45:
                approx_dir = constants.cardinal_directions[int(angle // 45)]
                break
        else:
            approx_dir = 'N'

        # Lanes preprocessing
        n_lanes: int = len(self.city_model[self.car_coordinates.axis0][self.car_coordinates.axis1].
                           lanes.get(self.current_direction))
        if n_lanes == 1:
            lane_type = lane_status(True, True)
        elif n_lanes == 0:
            lane_type = None
        elif self.current_lane == 0:
            lane_type = lane_status(True, False)
        elif self.current_lane == n_lanes - 1:
            lane_type = lane_status(False, True)
        else:
            lane_type = lane_status(False, False)

        # Whether the episode is finished
        is_done = self.car_coordinates.axis0 == self.destination_coordinates.axis0 and \
                  self.car_coordinates.axis1 == self.destination_coordinates.axis1

        return self.current_direction, approx_dir, lane_type, is_done
