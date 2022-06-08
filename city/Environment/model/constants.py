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
    'correct_stop',
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
    'turn_to_appropriate_direction',
    'turn_around_on_road',
    'positive_turn_around',
    'basic_left_right',
    'left_change_lane',
    'right_change_lane',
    'basic_forward',
    'forward_in_correct_direction',
    'turn_from_the_appropriate_lane',
    'reached_destination'
))
rewards = Rewards(
    visited_state=0,
    repeated_left_right=-10000,
    solid_line_crossing=-20000,
    out_of_road=-50000,
    turn_on_road=-30000,
    stop_in_the_middle_road=-10000,
    change_lane_not_on_road=0,
    correct_stop=+5000,

    left_change_lane=-300,
    right_change_lane=-140,

    wrong_lane_to_turn=-200,
    basic_left_right=-6525,
    turn_from_the_appropriate_lane=+590,
    tricky_turn=-20000,
    turn_to_appropriate_direction=500,


    basic_forward=-250,
    forward_in_correct_direction=+260,

    turn_around_through_solid_line=-25500,
    turn_around_on_intersection=-700,
    turn_around_on_road=-8000,
    basic_turn_around=-10000,
    positive_turn_around=9500,

    reached_destination=100000
)

close = dict()
close['N'] = ('W', 'NW', 'N', 'NE', 'E')
close['W'] = ('W', 'NW', 'N', 'SW', 'S')
close['E'] = ('S', 'SE', 'N', 'NE', 'E')
close['S'] = ('W', 'SW', 'S', 'SE', 'E')

closest = dict()
closest['N'] = ('NW', 'N', 'NE')
closest['W'] = ('W', 'NW', 'SW')
closest['E'] = ('SE', 'NE', 'E')
closest['S'] = ('SW', 'S', 'SE')

map_models_folder_name = 'map_models'
