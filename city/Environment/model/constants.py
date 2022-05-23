from collections import namedtuple
import numpy as np

h_actions = ('FORWARD',
             'LEFT',
             'RIGHT',
             'LEFT_LANE',
             'RIGHT_LANE',
             'TURN_AROUND')
actions = namedtuple('Actions', h_actions)(*np.arange(len(h_actions)))

next_direction = {'N': ['N', 'W', 'E', 'N', 'N', 'N', 'S'],
                  'W': ['W', 'S', 'N', 'W', 'W', 'W', 'E'],
                  'E': ['E', 'N', 'S', 'E', 'E', 'E', 'W'],
                  'S': ['S', 'E', 'W', 'S', 'S', 'S', 'N']}

cardinal_directions = ('SE', 'S', 'SW', 'W', 'NW', 'N', 'NE', 'E')

oriented_directions = {'v': 'NS', 'h': 'WE'}

rewards = namedtuple('Rewards', (
    'basic',
    'out_of_road',
    'turn_on_road',
    'turn_on_intersection',
    'solid_line_crossing',
    'change_lane_not_on_road',
    'wrong_lane_to_turn'
))(-10, -500, -400, -400, -300, -250, -250)
