import dill as pickle
import sys

from Environment.city import City
from Environment.model.utils import *
from Environment.model.constants import *
from Environment.model.state import State

import numpy as np


class Agent:
    """
    Class implements the Agent which interacts with underlying Environment called City.
    Represents a car which takes the particular action from action space and receives a feedback from the Environment.

    Parameters
    ----------
    map_sample : int,
        The ordinal number of map which is used to build the City

    layout_sample : int,
        The ordinal number of layout which describes the current map sample

    Attributes
    ----------
    env : City,
        In terms of RL, the Environment which Agent interacts with and defines Agent's policy.

    state : State,
        The current state of Agent within the underlying Environment.

    q_table : dict[State, dict[int, int]],
        The dictionary of all possible states which keeps an array with Q_values for every action from action space,
            which define a policy.
    """

    def __init__(self, map_sample: int = 0, layout_sample: int = 0):
        self.env = City(map_sample, layout_sample)
        self.state = self.env.reset()
        self.q_table: dict[State, list[int, int]] = \
            {state: [0 for _ in range(len(actions))] for state in self.env.states}
        self.last_action = None
        self.visited_states = set()

    def train(self, n_episodes: int = 100, alpha: float = 0.7, gamma: float = 0.7, epsilon: float = 0.8) -> None:
        """
        Performs a learning session which modifies agent's q_table and builds a behavioural policy.

        Parameters
        ----------
        n_episodes : int, default=100,
            The number of random episodes to learn

        alpha : float,  default=0.7,
            The value between (0; 1).
            The greater the value, the more emphasis is placed on our current Reward and discounted future Q_value.
            If the coefficient is small, Agent focuses on previous experience (already existing Q_value).

        gamma : float, default=0.7,
            Recommended between (0; 1).
            The coefficient which is used to discount Q_value of the following State.
            The greater this value, the more focus is placed on future success.

        epsilon : float, default=0.8,
            The value between (0; 1).
            Represents the probability of choosing the random action instead of using past experience.
            Helps to maintain the tradeoff between exploration and exploitation.

        Returns
        -------
        None - since the Agent's attribute is changed.
        """
        for episode in range(n_episodes):
            self.state = self.env.reset()

            is_done = False

            self.last_action = None
            self.visited_states = set()

            sum_reward = 0

            while not is_done:
                if np.random.uniform(0, 1) < epsilon:
                    action = sample(actions)  # Explore
                else:
                    if len(set(self.q_table[self.state])) == 1:
                        action = sample(actions)  # Explore
                    else:
                        for a in range(len(actions)):
                            if self.q_table[self.state][a] == 0:
                                self.q_table[self.state][a] = MIN_REWARD
                        action = np.argmax(self.q_table[self.state])  # Exploit
                        for a in range(len(actions)):
                            if self.q_table[self.state][a] == MIN_REWARD:
                                self.q_table[self.state][a] = 0

                next_state: State
                next_state, reward, is_done = self.env.step(action)

                # print(self.state)
                _data = (next_state.current_direction, next_state.car_coordinates)
                if _data in self.visited_states:
                    reward += rewards.visited_state
                    is_done = True
                    # print("ALREADY VISITED!", file=sys.stderr)
                else:
                    self.visited_states.add(_data)

                if self.last_action is not None and \
                        (self.last_action == actions.LEFT and action == actions.LEFT or
                         self.last_action == actions.RIGHT and action == actions.RIGHT or
                         self.last_action == actions.LEFT and action == actions.RIGHT or
                         self.last_action == actions.RIGHT and action == actions.LEFT):
                    reward += rewards.repeated_left_right

                self.last_action = action

                old_value = self.q_table[self.state][action]

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

    def perform(self, n_episodes: int = 100):
        """
        Test agent's performance on n_episodes different initial states and prints the number of successful and
        absolutely successful trials.
        """
        c = 0
        next_to_border = 0
        for episode in range(n_episodes):
            self.state = self.env.reset()
            print('INITIAL STATE:\n', self.state)

            is_done = False

            sum_reward = 0

            while not is_done:
                # action = np.argmax(agent.q_table[agent.state])
                if np.random.uniform(0, 1) < 0.999:
                    action = np.argmax(self.q_table[self.state])
                else:
                    action = np.random.choice(np.argpartition(self.q_table[self.state], -2)[-2:])

                print('action =', action)

                next_state, reward, is_done = self.env.step(action)

                if next_state.car_coordinates.axis0 == next_state.destination_coordinates.axis0 and \
                        next_state.car_coordinates.axis1 == next_state.destination_coordinates.axis1:
                    if next_state.current_lane == 0:
                        next_to_border += 1
                    c += 1

                sum_reward += reward
                self.state = next_state
                self.env.state = next_state

            print(f"Episode {episode}: {sum_reward = }\n\n")
        print(f"{c}/{n_episodes} objects reached their destination. Where {next_to_border = }")

    def reset(self):
        self.state = self.env.reset()
        self.q_table: dict[State, dict[int, int]] = \
            {state: [0 for _ in range(len(actions))] for state in self.env.states}
        self.last_action = None
        self.visited_states = set()

    def load_q_table_from_file(self, filename: str):
        with open('learning_data\\' + filename, 'rb') as q_file:
            self.q_table = pickle.load(q_file)

    def write_q_table_to_file(self, filename: str):
        with open('learning_data\\' + filename, 'wb') as q_file:
            pickle.dump(self.q_table, q_file)

    def compress_q_table(self, strategy: str = 'max') -> dict:
        compressed_q_table: dict = dict()
        for state in self.q_table.keys():
            compressed_q_table[state.to_transition_state()]: list = list()
        for state in self.q_table.keys():
            compressed_q_table[state.to_transition_state()].append(self.q_table[state])
        for transition_state in compressed_q_table.keys():
            q_pool_for_all_actions = np.array(compressed_q_table[transition_state])
            generalized_q_values = []
            for n_a in range(self.env.n_actions):
                q_values = q_pool_for_all_actions[:, n_a]
                q_values = q_values[q_values != MIN_REWARD]
                if q_values.size == 0:
                    q_value = MIN_REWARD
                else:
                    if strategy == 'max':
                        q_value = np.max(q_values)
                    elif strategy == 'mean':
                        q_value = np.mean(q_values)
                    elif strategy == 'min':
                        q_value = np.min(q_values)
                    else:
                        raise ValueError('Wrong strategy to compress q_table')

                generalized_q_values.append(q_value)
            compressed_q_table[transition_state] = generalized_q_values
        return compressed_q_table

    def extract_q_table(self, compressed_q_table: dict):
        for state in self.q_table.keys():
            try:
                self.q_table[state] = compressed_q_table[state.to_transition_state()]
            except KeyError:
                self.q_table[state] = [0] * self.env.n_actions

    @staticmethod
    def load_compressed_q_table_from_file(filename: str) -> dict:
        with open('learning_data\\' + filename, 'rb') as q_file:
            compressed_q_table = pickle.load(q_file)
        return compressed_q_table

    @staticmethod
    def write_compressed_q_table_to_file(filename: str, compressed_q_table: dict):
        with open('learning_data\\' + filename, 'wb') as q_file:
            pickle.dump(compressed_q_table, q_file)