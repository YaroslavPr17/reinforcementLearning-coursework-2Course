import math
import sys
from pathlib import Path
from typing import Union
from collections import namedtuple
from itertools import product
from tqdm import tqdm
import os


import numpy as np
from gym.spaces.discrete import Discrete

from Environment.objects.ground import Ground
from Environment.objects.intersection import Intersection
from Environment.objects.model_object import Object
from Environment.objects.road import Road
from Environment.objects.car import Car
from Environment.model import constants
from Environment.model.constants import actions
from Environment.model.state import lane_status
from Environment.model.state import State
from Environment.model.utils import *

map_path = Path("Environment", "raw_data")

iteration = 1
rep_array = [-1 for _ in range(5)]


def _observation(city_model: list, direction: str, car_coord: CarCoord, normalize: bool = False) -> np.ndarray:
    o = []
    axis0, axis1 = car_coord.axis0, car_coord.axis1

    if direction == 'N':
        for a0 in range(axis0 - 1, axis0 + 1):
            for a1 in range(axis1 - 1, axis1 + 2):
                o.append(city_model[a0][a1])
        obs = np.array(o).reshape(2, 3)
    elif direction == 'S':
        # print(axis0, axis1)
        for a0 in range(axis0, axis0 + 2):
            for a1 in range(axis1 - 1, axis1 + 2):
                if isinstance(city_model[a0][a1], Road):
                    o.append(city_model[a0][a1].swap_directions())
                else:
                    o.append(city_model[a0][a1])
        obs = np.array(o).reshape(2, 3)
    elif direction == 'W':
        for a0 in range(axis0 - 1, axis0 + 2):
            for a1 in range(axis1 - 1, axis1 + 1):
                if isinstance(city_model[a0][a1], Road):
                    o.append(city_model[a0][a1].swap_directions())
                else:
                    o.append(city_model[a0][a1])
        obs = np.array(o).reshape(3, 2)
    else:
        for a0 in range(axis0 - 1, axis0 + 2):
            for a1 in range(axis1, axis1 + 2):
                o.append(city_model[a0][a1])
        obs = np.array(o).reshape(3, 2)

    if normalize:
        if direction == 'W':
            obs = np.rot90(obs, 3)
        elif direction == 'E':
            obs = np.rot90(obs, 1)
        elif direction == 'S':
            obs = np.rot90(obs, 2)
    return obs


class City:

    np.random.seed(123)

    def __init__(self, map_sample: int = 0, layout_sample: int = 0, narrowing_and_expansion: bool = True):

        from Environment.raw_data.roads import roads

        city_map = []
        map_name = os.listdir(r'Environment\raw_data')[map_sample]
        with open(Path('Environment', 'raw_data', map_name), 'r') as map_file:
            line = map_file.readline()
            while line:
                city_map.append(line.split())
                line = map_file.readline()
        self.city_map = np.array(city_map)
        # print(f"{self.city_map = }")
        self.shape = self.city_map.shape

        self.intersections = np.array(list(zip(*np.where(self.city_map == 'X'))))
        self.roads = roads.get(layout_sample)
        # print(f"{self.intersections = }")
        # print(f"{self.roads = }")
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

        self.print_model_to_file(map_name[0:-4] + 'model.txt')

        # self.reward_range = np.arange()

        n_states = 0
        n_actions = len(constants.actions)
        self.n_actions = n_actions
        self.action_space = Discrete(n_actions)

        self.P = dict()
        self.states = []

        # print(f"{len(self.road_cells + list(map(tuple, self.intersections.astype(tuple))))}")
        for car_road_cell in self.road_cells + list(map(tuple, self.intersections.astype(tuple))):

            _road: Union[Road, list[Object]] = self.city_model[car_road_cell[0]][car_road_cell[1]]
            car_coord = CarCoord(car_road_cell[0], car_road_cell[1])

            # print(f"{len('NWES') = }")
            for direction in 'NWES': # constants.oriented_directions[_road.orientation]:
                observation = _observation(self.city_model, direction, car_coord, normalize=True)

                # print(f"{len(self.road_cells) = }")
                for dest_road_cell in self.road_cells:

                    dest_coord = DestCoord(dest_road_cell[0], dest_road_cell[1])

                    if isinstance(_road, Intersection):
                        n_lanes = 5
                        # print(car_coord, "Intersection!", n_lanes, '- lanes max')
                    else:
                        n_lanes = _road.n_lanes.get(direction)
                    if n_lanes is not None and n_lanes != 0:
                        n_lanes = range(n_lanes)
                    else:
                        n_lanes = (None,)
                    for lane in tuple(n_lanes) + (None,):
                        state = State(self.city_model, direction, car_coord, dest_coord, lane, observation)

                        for action in actions:

                            # if car_road_cell == (31, 29) and direction == 'W' and dest_road_cell == (13, 33) and lane == 0:
                            #     print("IN MODEL: ", hash(state), f"{action = }")
                            if action == actions.FORWARD:
                                new_state, reward, is_done = state.forward()
                            elif action == actions.LEFT:
                                new_state, reward, is_done = state.left()
                            elif action == actions.RIGHT:
                                new_state, reward, is_done = state.right()
                            elif action == actions.LEFT_LANE:
                                new_state, reward, is_done = state.left_lane()
                            elif action == actions.RIGHT_LANE:
                                new_state, reward, is_done = state.right_lane()
                            elif action == actions.TURN_AROUND:
                                new_state, reward, is_done = state.turn_around()
                            else:
                                print("Unexpected action!")

                            # if car_road_cell == (31, 29) and direction == 'W' and dest_road_cell == (13, 33) and lane == 0:
                            #     print("IN MODEL: ", state.__hash__())
                            #     print(state)

                            if state not in self.P.keys():
                                self.P[state] = dict()
                                n_states += 1
                                self.states.append(state)
                            self.P[state][action] = (new_state, reward, is_done)

        print('Transition dictionary was built.')

        self.n_states = n_states
        self.state = None
        self.learning_state = None

    @property
    def all_observations(self):
        obs = []
        for road_cell in self.road_cells:
            if self.city_model[road_cell[0]][road_cell[1]].orientation == 'v':
                for orientation in ('N', 'S'):
                    obs.append(_observation(self.city_model, orientation, CarCoord(*road_cell), normalize=True))
            else:
                for orientation in ('W', 'E'):
                    obs.append(_observation(self.city_model, orientation, CarCoord(*road_cell), normalize=True))
        return obs

    @property
    def _random_road(self):
        np.random.seed(None)
        return self.road_cells[np.random.randint(0, len(self.road_cells))]

    # May appear a problem if there are no lanes in the particular direction.
    def _generate_initial_state(self):
        np.random.seed(None)
        axis0, axis1 = self._random_road

        if self.city_model[axis0][axis1].orientation == 'v':
            direction = np.random.choice(['N', 'S'])
        else:
            direction = np.random.choice(['W', 'E'])

        lane = np.random.randint(0, len(self.city_model[axis0][axis1].lanes.get(direction)))

        car_coord = CarCoord(axis0, axis1)

        dest_coord = DestCoord(*self._random_road)

        observation = _observation(self.city_model, direction, car_coord, normalize=True)

        return State(self.city_model, direction, car_coord, dest_coord, lane, observation)

    def reset(self) -> State:
        self.state: State = self._generate_initial_state()
        return self.state

    def _make_intersections(self):
        for axis0, axis1 in self.intersections:
            self.city_model[axis0][axis1] = Intersection()

    def _make_roads(self, narrowing_and_expansion: bool = False) -> None:
        np.random.seed(123)
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
                intersection_start.n_lanes['E'] = 2
                intersection_finish.n_lanes['W'] = 2

                current_e_lanes = narrow_expand(intersection_start.n_lanes['E'])
                current_w_lanes = narrow_expand(intersection_finish.n_lanes['W'])

                for axis1_index in range(start_axis1 + 1, (finish_axis1 + start_axis1 + 1) // 2):
                    self.road_cells.append((start_axis0, axis1_index))
                    self.city_model[start_axis0][axis1_index] = Road('h',
                                                                     {'W': intersection_finish.n_lanes['W'],
                                                                      'E': intersection_start.n_lanes['E']},
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

                intersection_finish.n_lanes['W'] = current_w_lanes

            elif start_axis1 == finish_axis1:
                intersection_start.n_lanes['S'] = 3
                intersection_finish.n_lanes['N'] = 3

                current_n_lanes = narrow_expand(intersection_finish.n_lanes['N'])
                current_s_lanes = narrow_expand(intersection_start.n_lanes['S'])

                for axis0_index in range(start_axis0 + 1, (finish_axis0 + start_axis0 + 1) // 2):
                    self.road_cells.append((axis0_index, start_axis1))
                    self.city_model[axis0_index][start_axis1] = Road('v',
                                                                     {'N': intersection_finish.n_lanes['N'],
                                                                      'S': intersection_start.n_lanes['S']},
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

                intersection_finish.n_lanes['N'] = current_n_lanes

    def print_model_to_file(self, filename: str):
        with open(Path('Environment', filename), 'w', encoding='UTF-8') as new_map_file:
            for line in self.city_model:
                print(*line, sep='', file=new_map_file)

    def step(self, action: int) -> tuple:
        new_state, reward, is_done = self.P[self.state][action]
        return new_state, reward, is_done
