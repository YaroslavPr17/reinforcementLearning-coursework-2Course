from gym.spaces.discrete import Discrete
import numpy as np
from pathlib import Path
from Environment.objects.ground import Ground
from Environment.objects.intersection import Intersection
from Environment.objects.model_object import Object
from Environment.objects.road import Road

map_path = Path("Environment", "maps")


class City:
    def __init__(self):
        num_actions = 10
        self.action_space = Discrete(num_actions)

        city_map = []
        with open(Path(map_path, 'map.txt'), 'r') as map_file:
            line = map_file.readline()
            while line:
                city_map.append(line.split())
                line = map_file.readline()
        self.city_map = np.array(city_map)
        self.shape = self.city_map.shape

        self.city_model = [[Object() for _ in range(self.shape[1])] for _ in range(self.shape[0])]
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                self.city_model[i][j] = Ground()

        self.intersections = np.array(list(zip(*np.where(self.city_map == 'X'))))

        print('Empty city was built. (only ground)')

    def make_roads(self, connected_intersections: np.ndarray) -> None:
        for way in connected_intersections:

            intersection_start = self.intersections[way[0]]
            intersection_finish = self.intersections[way[1]]

            start_axis0 = intersection_start[0]
            start_axis1 = intersection_start[1]
            finish_axis0 = intersection_finish[0]
            finish_axis1 = intersection_finish[1]

            if not isinstance(self.city_model[start_axis0][start_axis1], Intersection):
                self.city_model[start_axis0][start_axis1] = Intersection(())
            if not isinstance(self.city_model[finish_axis0][finish_axis1], Intersection):
                self.city_model[finish_axis0][finish_axis1] = Intersection(())

            if start_axis0 == finish_axis0:
                if start_axis1 < finish_axis1:
                    self.city_model[start_axis0][start_axis1].road_dir += ('E',)
                    self.city_model[finish_axis0][finish_axis1].road_dir += ('W',)
                    for axis1_index in range(start_axis1 + 1, finish_axis1):
                        self.city_model[start_axis0][axis1_index] = Road()
                else:
                    self.city_model[start_axis0][start_axis1].road_dir += ('W',)
                    self.city_model[finish_axis0][finish_axis1].road_dir += ('E',)
                    for axis1_index in range(finish_axis1 + 1, start_axis1):
                        self.city_model[start_axis0][axis1_index] = Road()
            elif start_axis1 == finish_axis1:
                if start_axis0 < finish_axis0:
                    self.city_model[start_axis0][start_axis1].road_dir += ('S',)
                    self.city_model[finish_axis0][finish_axis1].road_dir += ('N',)
                    for axis0_index in range(start_axis0 + 1, finish_axis0):
                        self.city_model[axis0_index][start_axis1] = Road()
                else:
                    self.city_model[start_axis0][start_axis1].road_dir += ('N',)
                    self.city_model[finish_axis0][finish_axis1].road_dir += ('S',)
                    for axis0_index in range(finish_axis0 + 1, start_axis0):
                        self.city_model[axis0_index][start_axis1] = Road()

        print('Roads and intersections were built.')

    def print_map_to_file(self, filename: str):
        with open(Path(map_path, filename), 'w') as new_map_file:
            for line in self.city_map:
                print(' '.join(line), file=new_map_file, sep='\n')

    def print_model_to_file(self, filename: str):
        with open(Path('Environment', filename), 'w') as new_map_file:
            for line in self.city_model:
                print(*line, sep='', file=new_map_file)

    def step(self):
        pass

    def reset(self):
        pass
