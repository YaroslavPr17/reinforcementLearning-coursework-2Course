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

    'out_of_road',
    'solid_line_crossing',
    'turn_on_road',
    'stop_in_the_middle_road',
    'change_lane_not_on_road',
    'turn_around_on_intersection',
    'wrong_lane_to_turn',
    'basic_turn_around_on_road',
    'basic',
    'finished'
))(
    -10000,
    -5000,
    -4000,
    -4000,
    -2000,
    -1000,
    -1000,
    -2400,
    -300,
    10000
)
