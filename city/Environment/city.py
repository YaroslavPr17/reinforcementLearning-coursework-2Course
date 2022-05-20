import math
from pathlib import Path
from typing import Union
from collections import namedtuple
from itertools import product

import numpy as np
from gym.spaces.discrete import Discrete

from Environment.objects.ground import Ground
from Environment.objects.intersection import Intersection
from Environment.objects.model_object import Object
from Environment.objects.road import Road
from Environment.objects.car import Car
from Environment.model import constants
from Environment.model.state import lane_status
from Environment.model.state import State
from Environment.model.utils import *

raw_data_path = Path("Environment", "raw_data")


class City:

    def __init__(self, map_sample: int = 0, layout_sample: int = 0, narrowing_and_expansion: bool = False):

        from Environment.raw_data.roads import roads

        np.random.seed(123)

        city_map = []
        with open(Path(raw_data_path, 'map.txt'), 'r') as map_file:
            line = map_file.readline()
            while line:
                city_map.append(line.split())
                line = map_file.readline()
        self.city_map = np.array(city_map)
        self.shape = self.city_map.shape

        self.intersections = np.array(list(zip(*np.where(self.city_map == 'X'))))
        self.roads = roads.get(layout_sample)
        self.road_cells = []

        self.city_model = [[Object() for __ in range(self.shape[1])] for _ in range(self.shape[0])]
        print("Empty city was built.")

        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                self.city_model[i][j] = Ground()
        print("Ground was built.")

        self._make_intersections()
        self._make_roads(narrowing_and_expansion)
        print("Intersections and roads were built.")

        self.print_model_to_file('model_with_intersections_and_lanes(with dynamic lanes).txt')

        # self.reward_range = np.arange()

        # n_states =
        n_actions = len(constants.actions)
        self.action_space = Discrete(n_actions)

        self.P = dict()

        for d in constants.cardinal_directions[1::2]:
            for c_d in constants.cardinal_directions:
                for ln in [lane_status(*i) for i in product((True, False), repeat=2)]:
                    for done in [True, False]:
                        state = (d, c_d, ln, done)
                        self.P[state] = {i: [] for i in range(len(constants.actions))}

    @property
    def _random_road(self):
        return self.road_cells[np.random.randint(0, len(self.road_cells))]

    # May appear a problem if there are no lanes in the particular direction.
    def _generate_initial_state(self):
        axis0, axis1 = self._random_road

        if self.city_model[axis0][axis1].orientation == 'v':
            direction = np.random.choice(['N', 'S'])
        else:
            direction = np.random.choice(['W', 'E'])

        lane = np.random.randint(0, len(self.city_model[axis0][axis1].lanes.get(direction)))

        car_coord = CarCoord(axis0, axis1)

        dest_coord = DestCoord(*self._random_road)

        observation = self._observation(direction, car_coord)
        if direction in ('W', 'E'):
            observation = np.reshape(observation, (3, 2))
            if direction == 'W':
                observation = np.rot90(observation, 3)
            else:
                observation = np.rot90(observation, 1)
        else:
            observation = np.reshape(observation, (2, 3))
            if direction == 'S':
                observation = np.rot90(observation, 2)

        return State(self.city_model, direction, car_coord, dest_coord, lane, observation)

    def _observation(self, direction: str, car_coord: CarCoord) -> np.ndarray:
        o = []
        axis0, axis1 = car_coord.axis0, car_coord.axis1
        if direction == 'N':
            for a0 in range(axis0 - 1, axis0 + 1):
                for a1 in range(axis1 - 1, axis1 + 2):
                    o.append(self.city_model[a0][a1])
            return np.array(o).reshape(2, 3)
        elif direction == 'S':
            for a0 in range(axis0, axis0 + 2):
                for a1 in range(axis1 - 1, axis1 + 2):
                    o.append(self.city_model[a0][a1])
            return np.array(o).reshape(2, 3)
        elif direction == 'W':
            for a0 in range(axis0 - 1, axis0 + 2):
                for a1 in range(axis1 - 1, axis1 + 1):
                    o.append(self.city_model[a0][a1])
            return np.array(o).reshape(3, 2)
        else:
            for a0 in range(axis0 - 1, axis0 + 2):
                for a1 in range(axis1, axis1 + 2):
                    o.append(self.city_model[a0][a1])
            return np.array(o).reshape(3, 2)

    def reset(self) -> State:
        return self._generate_initial_state()

    def _make_intersections(self):
        for axis0, axis1 in self.intersections:
            self.city_model[axis0][axis1] = Intersection()

    def _make_roads(self, narrowing_and_expansion: bool = False) -> None:
        _LANES_AVAILABLE = [1, 2, 3]
        _LANE_TRANSFORMATIONS = [-1, 0, 1]

        def narrow_expand(n_lanes: int) -> int:
            if narrowing_and_expansion and n_lanes >= 2:
                shift = np.random.choice(_LANE_TRANSFORMATIONS)
                return n_lanes + shift
            return n_lanes

        for way in self.roads:

            intersection_start_coord = self.intersections[way[0]]
            intersection_finish_coord = self.intersections[way[1]]

            start_axis0 = intersection_start_coord[0]
            start_axis1 = intersection_start_coord[1]
            finish_axis0 = intersection_finish_coord[0]
            finish_axis1 = intersection_finish_coord[1]

            intersection_start: Union[Intersection, list[Object]] = self.city_model[start_axis0][start_axis1]
            intersection_finish: Union[Intersection, list[Object]] = self.city_model[finish_axis0][finish_axis1]

            if start_axis0 == finish_axis0:
                intersection_start.lanes['E'] = 2
                intersection_finish.lanes['W'] = 2

                current_e_lanes = narrow_expand(intersection_start.lanes['E'])
                current_w_lanes = narrow_expand(intersection_finish.lanes['W'])

                for axis1_index in range(start_axis1 + 1, (finish_axis1 + start_axis1 + 1) // 2):
                    self.road_cells.append((start_axis0, axis1_index))
                    self.city_model[start_axis0][axis1_index] = Road('h',
                                                                     {'W': intersection_finish.lanes['W'],
                                                                      'E': intersection_start.lanes['E']},
                                                                     'ds',
                                                                     'b')
                for axis1_index in range((finish_axis1 + start_axis1 + 1) // 2, finish_axis1):
                    self.road_cells.append((start_axis0, axis1_index))
                    self.city_model[start_axis0][axis1_index] = \
                        Road('h',
                             {'W': current_w_lanes,
                              'E': current_e_lanes},
                             'ds',
                             'b')

                intersection_finish.lanes['W'] = current_w_lanes

            elif start_axis1 == finish_axis1:
                intersection_start.lanes['S'] = 3
                intersection_finish.lanes['N'] = 3

                current_n_lanes = narrow_expand(intersection_finish.lanes['N'])
                current_s_lanes = narrow_expand(intersection_start.lanes['S'])

                for axis0_index in range(start_axis0 + 1, (finish_axis0 + start_axis0 + 1) // 2):
                    self.road_cells.append((axis0_index, start_axis1))
                    self.city_model[axis0_index][start_axis1] = Road('v',
                                                                     {'N': intersection_finish.lanes['N'],
                                                                      'S': intersection_start.lanes['S']},
                                                                     'ds',
                                                                     'b')

                for axis0_index in range((finish_axis0 + start_axis0 + 1) // 2, finish_axis0):
                    self.road_cells.append((axis0_index, start_axis1))
                    self.city_model[axis0_index][start_axis1] = \
                        Road('v',
                             {'N': current_n_lanes,
                              'S': current_s_lanes},
                             'ds',
                             'b')

                intersection_finish.lanes['N'] = current_n_lanes

    def print_model_to_file(self, filename: str):
        with open(Path('Environment', filename), 'w', encoding='UTF-8') as new_map_file:
            for line in self.city_model:
                print(*line, sep='', file=new_map_file)

    def step(self):
        pass

    def check_traffic_regulations(self, observation: tuple):
        pass
