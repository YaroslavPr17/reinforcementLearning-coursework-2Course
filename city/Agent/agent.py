from Environment.city import City

from collections import namedtuple
import numpy as np


class Agent:
    """
    Class for agent in Reinforcement learning project.

    0 - move forward
    1 - move right
    2 - move back
    3 - move left
    4 - change lane to left
    5 - change lane to right
    6 - pass
    7 - turn around


    """

    def __init__(self):
        self.env = City(narrowing_and_expansion=True)

