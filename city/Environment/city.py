import math
import sys
from pathlib import Path
from typing import Union
from collections import namedtuple
from itertools import product
from tqdm import tqdm
import os

from Environment.objects.ground import Ground
from Environment.objects.intersection import Intersection
from Environment.objects.model_object import Object
from Environment.objects.road import Road
from Environment.model import constants
from Environment.model.constants import *
from Environment.model.state import State
from Environment.model.utils import *




def get_observation(city_model: list, direction: str, car_coord: CarCoord, normalize: bool = False) -> np.ndarray:
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


class City:

    np.random.seed(123)

    def __init__(self, map_sample: int = 0, layout_sample: int = 0, narrowing_and_expansion: bool = True):

        from Environment.raw_data.roads_descriptor import roads_desc

        city_map = []
        map_name = os.listdir(Path('Environment', 'raw_data'))[map_sample]
        with open(Path('Environment', 'raw_data', map_name), 'r') as map_file:
            line = map_file.readline()
            while line:
                city_map.append(line.split())
                line = map_file.readline()
        self.city_map = np.array(city_map)
        self.shape = self.city_map.shape

        self.intersections = np.array(list(zip(*np.where(self.city_map == 'X'))))
        self.roads = roads_desc.get(map_sample).get(layout_sample)
        self.road_cells = []

        self.city_model = [[Object() for __ in range(self.shape[1])] for _ in range(self.shape[0])]
        print("Empty city was built.")

        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                self.city_model[i][j] = Ground()
        print("Ground was built.")

        self._make_intersections()
        print("Intersections were built.")
        self._make_roads(narrowing_and_expansion)
        print("Roads were built.")
        self._finalize_intersections()
        print("Intersections were finalized.")

        self.print_model_to_file(Path(map_models_folder_name, map_name[0:-4] + 'model.txt'))

        self.P = dict()
        self.states = []

        for car_road_cell in tqdm(self.road_cells + list(map(tuple, self.intersections.astype(tuple))), file=sys.stdout):

            _road: Union[Road, list[Object]] = self.city_model[car_road_cell[0]][car_road_cell[1]]
            car_coord = CarCoord(car_road_cell[0], car_road_cell[1])

            for direction in 'NWES':
                observation = get_observation(self.city_model, direction, car_coord, normalize=True)

                for dest_road_cell in self.road_cells:

                    dest_coord = DestCoord(dest_road_cell[0], dest_road_cell[1])

                    if isinstance(_road, Intersection):
                        n_lanes = constants.MAX_N_LANES
                    else:
                        n_lanes = _road.n_lanes.get(direction)
                    if n_lanes is not None and n_lanes != 0:
                        n_lanes = range(n_lanes)
                    else:
                        n_lanes = (None,)
                    for lane in tuple(n_lanes) + (None,):
                        state = State(self.city_model, direction, car_coord, dest_coord, lane, observation)

                        for action in actions:
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
                                raise ValueError('Unable to collect info about the following state.')

                            if state not in self.P.keys():
                                self.P[state] = dict()
                                self.states.append(state)
                            self.P[state][action] = (new_state, reward, is_done)

        print('Transition dictionary was built.')
        print(f'{sys.getsizeof(self.states) = }')
        print(f'{sys.getsizeof(self.P) = }')

        self.n_states = len(self.P.keys())
        self.n_actions = len(constants.actions)
        self.action_space = [a for a in range(self.n_actions)]

    @property
    def all_observations(self):
        obs = []
        for road_cell in self.road_cells:
            if self.city_model[road_cell[0]][road_cell[1]].orientation == 'v':
                for orientation in ('N', 'S'):
                    obs.append(get_observation(self.city_model, orientation, CarCoord(*road_cell), normalize=True))
            else:
                for orientation in ('W', 'E'):
                    obs.append(get_observation(self.city_model, orientation, CarCoord(*road_cell), normalize=True))
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

        observation = get_observation(self.city_model, direction, car_coord, normalize=True)

        return State(self.city_model, direction, car_coord, dest_coord, lane, observation)

    def reset(self) -> State:
        self.state: State = self._generate_initial_state()
        return self.state

    def _make_intersections(self):
        for axis0, axis1 in self.intersections:
            self.city_model[axis0][axis1] = Intersection()

    def _make_roads(self, narrowing_and_expansion: bool) -> None:
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

    def _finalize_intersections(self):
        iter_intersections = [IntersectCoord(*intersection_index) for intersection_index in self.intersections]
        for i in iter_intersections:
            local_intersection: Union[Intersection, list[Object]] = self.city_model[i.axis0][i.axis1]
            up_obj = self.city_model[i.axis0 - 1][i.axis1]
            down_obj = self.city_model[i.axis0 + 1][i.axis1]
            left_obj = self.city_model[i.axis0][i.axis1 - 1]
            right_obj = self.city_model[i.axis0][i.axis1 + 1]

            if isinstance(up_obj, Road):
                local_intersection.n_in_lanes['N'] = up_obj.n_lanes.get('S')
            if isinstance(left_obj, Road):
                local_intersection.n_in_lanes['W'] = left_obj.n_lanes.get('E')
            if isinstance(right_obj, Road):
                local_intersection.n_in_lanes['E'] = right_obj.n_lanes.get('W')
            if isinstance(down_obj, Road):
                local_intersection.n_in_lanes['S'] = down_obj.n_lanes.get('N')

    def print_model_to_file(self, filename: Path):
        with open(Path('Environment', filename), 'w', encoding='UTF-8') as new_map_file:
            for line in self.city_model:
                print(*line, sep='', file=new_map_file)

    def step(self, action: int) -> tuple:
        new_state, reward, is_done = self.P[self.state][action]
        return new_state, reward, is_done
