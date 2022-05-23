import math
import sys
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
from Environment.model.constants import actions
from Environment.model.state import lane_status
from Environment.model.state import State
from Environment.model.utils import *

raw_data_path = Path("Environment", "raw_data")


def _observation(city_model: list, direction: str, car_coord: CarCoord, normalize: bool = False) -> np.ndarray:
    o = []
    axis0, axis1 = car_coord.axis0, car_coord.axis1

    if direction == 'N':
        for a0 in range(axis0 - 1, axis0 + 1):
            for a1 in range(axis1 - 1, axis1 + 2):
                o.append(city_model[a0][a1])
        obs = np.array(o).reshape(2, 3)
    elif direction == 'S':
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

def closest(target_dir: str, dirs: list):
    directions = constants.cardinal_directions[1::2]
    distances = []
    for d in dirs:
        dist = abs(directions.index(target_dir) - directions.index(d))
        dist %= 5
        distances.append(dist)
    res = list(zip(dirs, distances))
    res = filter(lambda t: t[1] <= 1, res)
    res = [t[0] for t in res]
    return res


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

        n_states = 0
        n_actions = len(constants.actions)
        self.n_actions = n_actions
        self.action_space = Discrete(n_actions)

        self.P = dict()
        self.states = []

        # for car_road_cell in self.road_cells:
        #     print(self.road_cells.index(car_road_cell), end=' ')
        #     _road: Union[Road, list[Object]] = self.city_model[car_road_cell[0]][car_road_cell[1]]
        #     car_coord = CarCoord(car_road_cell[0], car_road_cell[1])
        #
        #     for direction in 'NWES': # constants.oriented_directions[_road.orientation]:
        #         observation = _observation(self.city_model, direction, car_coord, normalize=True)
        #
        #         for dest_road_cell in self.road_cells:
        #             dest_coord = DestCoord(dest_road_cell[0], dest_road_cell[1])
        #
        #             for lane in range(_road.n_lanes.get(direction)), None:
        #                 state = State(self.city_model, direction, car_coord, dest_coord, lane, observation)
        #
        #                 for action in actions:
        #                     if car_road_cell == (31, 29) and direction == 'W' and dest_road_cell == (13, 33) and lane == 0:
        #                         print("IN MODEL: ", hash(state), f"{action = }")
        #                     if action == actions.FORWARD:
        #                         new_state, reward, is_done = state.forward()
        #                     elif action == actions.LEFT:
        #                         new_state, reward, is_done = state.left()
        #                     elif action == actions.RIGHT:
        #                         new_state, reward, is_done = state.right()
        #                     elif action == actions.LEFT_LANE:
        #                         new_state, reward, is_done = state.left_lane()
        #                     elif action == actions.RIGHT_LANE:
        #                         new_state, reward, is_done = state.right_lane()
        #                     elif action == actions.TURN_AROUND:
        #                         new_state, reward, is_done = state.turn_around()
        #                     else:
        #                         new_state, reward, is_done = None, None, None
        #
        #                     # if car_road_cell == (31, 29) and direction == 'W' and dest_road_cell == (13, 33) and lane == 0:
        #                     #     print("IN MODEL: ", state.__hash__())
        #                     #     print(state)
        #
        #                     if state not in self.P:
        #                         self.P[state] = dict()
        #                         n_states += 1
        #                         self.states.append(state)
        #                     self.P[state][action] = (new_state, reward, is_done)


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

        observation = _observation(self.city_model, direction, car_coord, normalize=True)

        return State(self.city_model, direction, car_coord, dest_coord, lane, observation)

    def reset(self) -> State:
        self.state: State = self._generate_initial_state()
        return self.state

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

    def step(self, action):
        print(self.state in self.states)

        new_state, reward, is_done = self.P[self.state][action]
        return new_state, reward, is_done


    def check_traffic_regulations(self, observation: tuple):
        pass

    def move_car(self, direction: str, action: int):
        new_direction = constants.next_direction.get(direction)[action]
        if action == constants.actions.LEFT_LANE or actions.RIGHT_LANE:
            pass
        if direction == 'W':
            new_car_coord = CarCoord(self.state.car_coordinates.axis0, self.state.car_coordinates.axis1 - 1)
        elif direction == 'E':
            new_car_coord = CarCoord(self.state.car_coordinates.axis0, self.state.car_coordinates.axis1 + 1)
        elif direction == 'N':
            new_car_coord = CarCoord(self.state.car_coordinates.axis0 - 1, self.state.car_coordinates.axis1)
        elif direction == 'S':
            new_car_coord = CarCoord(self.state.car_coordinates.axis0 + 1, self.state.car_coordinates.axis1)
