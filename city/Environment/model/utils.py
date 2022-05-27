from collections import namedtuple
import numpy as np

CarCoord = namedtuple('CarCoord', 'axis0 axis1')
DestCoord = namedtuple('DestCoord', 'axis0 axis1')


def left(direction: str):
    """
    Chooses the closest cardinal direction on the left from the given one.

    Parameters
    ----------
    direction : str,
        One of four cardinal directions

    Returns
    -------
    str, One of four cardinal directions on the left
    """
    return dict(zip('NWES', 'WSNE')).get(direction)


def right(direction: str):
    """
    Chooses the closest cardinal direction on the right from the given one.

    Parameters
    ----------
    direction : str,
        One of four cardinal directions

    Returns
    -------
    str, One of four cardinal directions on the right
    """
    return dict(zip('NWES', 'ENSW')).get(direction)


def opposite(direction: str):
    """
    Chooses the opposite cardinal direction for the given one.

    Parameters
    ----------
    direction : str,
        One of four cardinal directions

    Returns
    -------
        One of four cardinal directions
    """
    return dict(zip('NWES', 'SEWN')).get(direction)


def sample(iterable_object):
    """
    Randomly chooses one of elements in given object.

    Parameters
    ----------
    iterable_object : list, tuple, etc.,
        any iterable object

    Returns
    -------
    Random element from the given iterable object
    """
    return np.random.choice(iterable_object)
