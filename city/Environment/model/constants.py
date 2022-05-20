from collections import namedtuple
import numpy as np

__actions = ('FORWARD',
             'RIGHT',
             'LEFT',
             'LEFT_LANE',
             'RIGHT_LANE',
             'PASS',
             'TURN_AROUND')
actions = namedtuple('Actions', __actions)(*np.arange(len(__actions)))

cardinal_directions = ('SE', 'S', 'SW', 'W', 'NW', 'N', 'NE', 'E')
