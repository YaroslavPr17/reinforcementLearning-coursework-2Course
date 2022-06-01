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
    'tricky_turn',
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
    'left_change_lane',
    'right_change_lane',
    'basic_forward',
    'forward_not_in_correct_direction',
    'turn_from_the_appropriate_lane',
    'reached_destination'
))
rewards = Rewards(
    visited_state=0,
    repeated_left_right=-10000,
    solid_line_crossing=-10000,
    out_of_road=-9000,
    turn_on_road=-8000,
    stop_in_the_middle_road=-5000,
    change_lane_not_on_road=0,

    left_change_lane=-500,
    right_change_lane=-400,

    wrong_lane_to_turn=-200,
    basic_left_right=-325,
    turn_from_the_appropriate_lane=90,
    tricky_turn=-57000,

    basic_forward=-300,
    forward_not_in_correct_direction=-75,

    turn_around_through_solid_line=-2500,
    turn_around_on_intersection=-700,
    turn_around_on_road=-1000,
    basic_turn_around=-2000,
    positive_turn_around=1900,

    reached_destination=100000
)

close = dict()
close['N'] = ('W', 'NW', 'N', 'NE', 'E')
close['W'] = ('W', 'NW', 'N', 'SW', 'S')
close['E'] = ('S', 'SE', 'N', 'NE', 'E')
close['S'] = ('W', 'SW', 'S', 'SE', 'E')
