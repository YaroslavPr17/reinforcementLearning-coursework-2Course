from Environment.city import City
from collections import defaultdict
from Environment.model.constants import actions
from Environment.model.utils import *
from Environment.model.constants import *
from Environment.model.state import State

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

GAMMA = 0.9
ALPHA = 0.2
EPSILON = 0.99

class Agent:
    def __init__(self):
        self.env = City(narrowing_and_expansion=True)
        self.state = self.env.reset()
        self.q_table: dict[State, dict[int, int]] = {state:{action: 0 for action in range(len(actions))} for state in self.env.states}

    def learn(self, n_episodes: int = 100):
        for episode in range(n_episodes):
            is_done = False

            sum_reward = 0

            while not is_done:
                if np.random.uniform(0, 1) < EPSILON:
                    action = sample(actions)                        # Explore
                else:
                    action = np.argmax(self.q_table[self.state])    # Exploit

                macro_keys = 0
                micro_keys = 0
                for s in self.env.P.keys():
                    macro_keys += 1
                    for a in self.env.P[s].keys():
                        micro_keys += 1

                print(f"{macro_keys = }, {micro_keys = }\n")

                print("IN LEARNING: ", self.env.state in self.env.states, hash(self.env.state))

                print(action)

                next_state, reward, is_done = self.env.step(action)

                old_value = self.q_table[self.state][action]
                next_max = np.max(self.q_table[next_state])

                new_value = (1 - ALPHA) * old_value + ALPHA * (reward + GAMMA * next_max)
                self.q_table[self.state][action] = new_value

                sum_reward += reward
                self.state = next_state

            print(f"Episode {episode}: {sum_reward = }")



