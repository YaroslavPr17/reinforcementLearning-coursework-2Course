from collections import namedtuple
from Environment.model.constants import actions
import numpy as np

CarCoord = namedtuple('CarCoord', 'axis0 axis1')
DestCoord = namedtuple('DestCoord', 'axis0 axis1')


def left(direction: str):
    return dict(zip('NWES', 'WSNE')).get(direction)


def right(direction: str):
    return dict(zip('NWES', 'ENSW')).get(direction)


def opposite(direction: str):
    return dict(zip('NWES', 'SEWN')).get(direction)


def sample(array):
    return np.random.choice(array)
