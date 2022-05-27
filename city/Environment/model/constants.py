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

Rewards = namedtuple('Rewards', (

    'solid_line_crossing',
    'out_of_road',
    'turn_around_through_solid_line',
    'turn_on_road',
    'stop_in_the_middle_road',
    'change_lane_not_on_road',
    'wrong_lane_to_turn',
    'basic_turn_around',
    'turn_around_on_intersection',
    'turn_around_on_road',
    'basic_left_right',
    'basic_change_lane',
    'basic_forward',
    'turn_from_the_appropriate_lane',
    'reached_destination'
))
rewards = Rewards(
    solid_line_crossing = -20000,
    out_of_road = -15000,
    turn_around_through_solid_line = -5000,
    turn_on_road = -7000,
    stop_in_the_middle_road = -7000,
    change_lane_not_on_road = -2000,
    wrong_lane_to_turn = -2000,
    basic_turn_around = -8000,
    turn_around_on_intersection = -1000,
    turn_around_on_road= -8000,
    basic_left_right = -6000,
    basic_change_lane = -500,
    basic_forward = 4500,
    turn_from_the_appropriate_lane = 500,
    reached_destination = 130000
)
