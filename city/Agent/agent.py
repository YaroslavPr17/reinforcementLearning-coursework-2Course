from Environment.city import City
from collections import defaultdict
from Environment.model.constants import actions
from Environment.model.utils import *
from Environment.model.constants import *
from Environment.model.state import State
from tqdm import tqdm

from collections import namedtuple
import numpy as np


# class Agent:
#     """
#     Class for agent in Reinforcement learning project.
#
#     0 - move forward
#     1 - move right
#     2 - move back
#     3 - move left
#     4 - change lane to left
#     5 - change lane to right
#     6 - pass
#     7 - turn around
#
#
#     """
#
#     def __init__(self):
#         self.env = City(narrowing_and_expansion=True)

GAMMA = 0.1
ALPHA = 0.3
EPSILON = 0.5

class Agent:
    def __init__(self, map_sample: int = 0, layout_sample: int = 0):
        self.env = City(map_sample, layout_sample)
        self.state = self.env.reset()
        self.q_table: dict[State, dict[int, int]] = {state:[0 for action in range(len(actions))] for state in self.env.states}

    def learn(self, n_episodes: int = 100, alpha: float = ALPHA, gamma: float = GAMMA, epsilon: float = EPSILON):

        for episode in range(n_episodes):
            self.state = self.env.reset()

            is_done = False

            sum_reward = 0

            while not is_done:
                if np.random.uniform(0, 1) < epsilon:
                    action = sample(actions)                            # Explore
                else:
                    if len(set(self.q_table[self.state])) == 1:
                        action = sample(actions)                        # Explore
                    else:
                        for a in range(len(actions)):
                            if self.q_table[self.state][a] == 0:
                                self.q_table[self.state][a] = -1000000
                        action = np.argmax(self.q_table[self.state])    # Exploit
                        for a in range(len(actions)):
                            if self.q_table[self.state][a] == -1000000:
                                self.q_table[self.state][a] = 0

                next_state, reward, is_done = self.env.step(action)

                old_value = self.q_table[self.state][action]

                # print(self.q_table[next_state])

                if is_done:
                    next_max = 0
                else:
                    next_max = np.max(self.q_table[next_state])


                new_value = (1 - alpha) * old_value + alpha * (reward + gamma * next_max)

                self.q_table[self.state][action] = new_value

                sum_reward += reward
                self.state = next_state
                self.env.state = next_state

            # print(f"Episode {episode}: {sum_reward = }")



