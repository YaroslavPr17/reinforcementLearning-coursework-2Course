from collections import namedtuple
from typing import Union

from Environment.model.constants import actions
import numpy as np

CarCoord = namedtuple('CarCoord', 'axis0 axis1')
DestCoord = namedtuple('DestCoord', 'axis0 axis1')


def left(direction: str):
    """
    Chooses the closest cardinal direction on the left from the given one
    :param direction: One of four cardinal directions
    :rtype: str
    :return: One of four cardinal directions on the left
    """
    return dict(zip('NWES', 'WSNE')).get(direction)


def right(direction: str):
    """
    Chooses the closest cardinal direction on the right from the given one
    :param direction: One of four cardinal directions
    :rtype: str
    :return: One of four cardinal directions on the right
    """
    return dict(zip('NWES', 'ENSW')).get(direction)


def opposite(direction: str):
    """
    Chooses the opposite cardinal direction for the given one
    :param direction: One of four cardinal directions
    :rtype: str
    :return: One of four cardinal directions
    """
    return dict(zip('NWES', 'SEWN')).get(direction)


def sample(iterable_object):
    """
    Randomly chooses one of elements in given object
    :param iterable_object: any iterable object
    :type iterable_object: list, tuple, etc.
    :return: Random element
    """
    return np.random.choice(iterable_object)
