from collections import namedtuple
import numpy as np

h_actions = ('FORWARD',
             'LEFT',
             'RIGHT',
             'LEFT_LANE',
             'RIGHT_LANE',
             'TURN_AROUND')
actions = namedtuple('Actions', h_actions)(*np.arange(len(h_actions)))

MAX_N_LANES = 5
MIN_REWARD = -1_000_000

next_direction = {'N': ['N', 'W', 'E', 'N', 'N', 'N', 'S'],
                  'W': ['W', 'S', 'N', 'W', 'W', 'W', 'E'],
                  'E': ['E', 'N', 'S', 'E', 'E', 'E', 'W'],
                  'S': ['S', 'E', 'W', 'S', 'S', 'S', 'N']}

cardinal_directions = ('SE', 'S', 'SW', 'W', 'NW', 'N', 'NE', 'E')

oriented_directions = {'v': 'NS', 'h': 'WE'}

Rewards = namedtuple('Rewards', (
    'visited_state',
    'repeated_left_right',
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
    'positive_turn_around',
    'basic_left_right',
    'basic_change_lane',
    'basic_forward',
    'turn_from_the_appropriate_lane',
    'reached_destination'
))
rewards = Rewards(
    visited_state=-200000,
    repeated_left_right=-70000,
    solid_line_crossing=-60000,
    out_of_road=-40000,
    turn_around_through_solid_line=-4000,
    turn_on_road=-40000,
    stop_in_the_middle_road=-20000,
    change_lane_not_on_road=-10000,
    wrong_lane_to_turn=-3000,
    basic_turn_around=-32000,
    turn_around_on_intersection=-3000,
    turn_around_on_road=-8000,
    positive_turn_around=+10000,
    basic_left_right=+100,
    basic_change_lane=-1500,
    basic_forward=+2500,
    turn_from_the_appropriate_lane=+5000,
    reached_destination=+100000
)
