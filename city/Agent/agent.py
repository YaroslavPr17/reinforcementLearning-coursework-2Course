import math
import sys
import time
from time import sleep
from collections import namedtuple

import dill as pickle
from tqdm import tqdm
from pathlib import Path

from Environment.city import City
from Environment.model.utils import *
from Environment.model.constants import *
from Environment.model.state import State
from graphics.env_vizualization import MapVizualization
from graphics.visual_process import Visualizer

data_filename = 'compressed_q_table'
path_to_learning_data = Path('learning_data', data_filename)


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

    def __init__(self, map_sample: int = 0, layout_sample: int = 0, graphics: bool = True):
        self.env = City(map_sample, layout_sample)

        self.q_table: dict[State, list[int]] = \
            {state: [0 for _ in range(len(actions))] for state in self.env.P.keys()}

        self.state = self.env.reset()

        self.is_demo = graphics
        if graphics:
            self.visualizer = Visualizer(self.env)
            self.visualizer.start()

    def training_session(self,
                         statistics: namedtuple("Statistics", "unvisited_states partially_visited_states episodes_count"),
                         n_episodes: int = 100000,
                         alpha: float = 0.7, gamma: float = 0.7, epsilon: float = 0.8,
                         ) -> None:
        """
        Performs a learning session which modifies agent's q_table and builds a behavioural policy.

        Parameters
        ----------
        unvisited_states : list
            The list of numbers of unvisited states over the whole learning process.

        partially_visited_states : list
            The list of numbers of partially visited states over the whole learning process.

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

        print(f"{alpha=} | {gamma=} | {epsilon=}")
        start_time = time.time()

        for episode in tqdm(range(n_episodes), file=sys.stdout):

            self.state = self.env.reset()

            is_done = False

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

        whole_zero = 0
        any_zero = 0
        for el in self.q_table.values():
            if all(map(lambda a: a == INITIAL_Q_VALUE, el)):
                whole_zero += 1
            if INITIAL_Q_VALUE in el:
                any_zero += 1
        statistics.unvisited_states.append(whole_zero)
        statistics.partially_visited_states.append(any_zero)
        statistics.episodes_count.append(n_episodes)
        finish_time = time.time()
        print(f"Wall time: {np.round(float(finish_time - start_time), 2)} seconds.\n")

    def train(self) -> namedtuple("Statistics", "unvisited_states partially_visited_states episodes_count"):
        Stat = namedtuple("Statistics", "unvisited_states partially_visited_states episodes_count")
        stat = Stat([], [], [0])

        whole_zero = 0
        any_zero = 0
        for el in self.q_table.values():
            if all(map(lambda a: a == INITIAL_Q_VALUE, el)):
                whole_zero += 1
            if INITIAL_Q_VALUE in el:
                any_zero += 1
        stat.unvisited_states.append(whole_zero)
        stat.partially_visited_states.append(any_zero)
        print("Overall number of states =", whole_zero)

        start_training_time = time.time()

        self.training_session(stat, 300000, alpha=1, gamma=0.9, epsilon=1)
        self.training_session(stat, 200000, alpha=1, gamma=0.9, epsilon=1)

        self.training_session(stat, 120000, alpha=0.7, gamma=0.9, epsilon=0.9)
        self.training_session(stat, 140000, alpha=0.5, gamma=0.9, epsilon=0.8)
        self.training_session(stat, 160000, alpha=0.35, gamma=0.9, epsilon=0.7)

        self.training_session(stat, 200000, alpha=0.3, gamma=0.9, epsilon=0.6)
        self.training_session(stat, 200000, alpha=0.3, gamma=0.9, epsilon=0.6)

        self.training_session(stat, 400000, alpha=0.3, gamma=0.9, epsilon=0.1)
        self.training_session(stat, 200000, alpha=0.3, gamma=0.9, epsilon=0.1)

        finish_training_time = time.time()

        print("Overall training time:", np.round(float(finish_training_time - start_training_time), 2), "seconds.")
        print("Numbers of unvisited states:\n", stat.unvisited_states)
        print("Numbers of partially visited states:\n", stat.partially_visited_states)

        self.finalize()

        return stat

    def perform(self, n_episodes: int = 100):
        """
        Test agent's performance on n_episodes different initial states and prints the number of successful and
        absolutely successful trials.
        """
        n_successful_trials = 0
        next_to_border = 0
        cycled = 0
        for episode in range(n_episodes):
            self.state = self.env.reset()
            # print('INITIAL STATE:\n', self.state)

            is_done = False

            sum_reward = 0

            time_value = time.time()

            while not is_done:
                # Graphic test callback
                MapVizualization.callback_agent_draw(self.state)

                if isinstance(np.argmax(self.q_table[self.state]), np.int64):
                    action = np.argmax(self.q_table[self.state])
                else:
                    action = list(np.argmax(self.q_table[self.state]))[0]

                next_state: State
                next_state, reward, is_done = self.env.step(action)

                # print(f'{action = }, lane = {next_state.current_lane}')
                # print(list(self.q_table[self.state]), end='\n\n')

                if not self.is_demo and time.time() - time_value > 1.5:
                    sum_reward = -10000
                    cycled += 1
                    break

                if next_state.car_coordinates.axis0 == next_state.destination_coordinates.axis0 and \
                        next_state.car_coordinates.axis1 == next_state.destination_coordinates.axis1:
                    if next_state.current_lane == 0:
                        next_to_border += 1
                    n_successful_trials += 1

                sum_reward += reward
                self.state = next_state
                self.env.state = next_state
                if self.is_demo:
                    sleep(3)
            print(f"Episode {episode}: {sum_reward = }")
        print(f"{n_successful_trials}/{n_episodes} objects reached their destination. Where {next_to_border = }")
        print(f"{cycled = }")

    def reset(self) -> None:
        """
        Resets current agent to initial state with no knowledge about environment.
        """
        self.state = self.env.reset()
        self.q_table: dict[State, dict[int, int]] = \
            {state: [0 for _ in range(len(actions))] for state in self.env.P.keys()}

    def load_q_table_from_file(self, filename: str) -> None:
        """
        Loads existing q_table from given file to agent's field.

        Parameters
        ----------
        filename : str,
            The file from which q_table will be read.
        """

        with open('learning_data\\' + filename, 'rb') as q_file:
            self.q_table = pickle.load(q_file)

    def write_q_table_to_file(self, filename: str):
        """
        Creates a dump of q_values to the file of given name.

        Parameters
        ----------
        filename : str,
            The filename where q_values will be stored.
        """

        with open('learning_data\\' + filename, 'wb') as q_file:
            pickle.dump(self.q_table, q_file)

    def compress_q_table(self) -> dict:
        """
        Performs mapping of existing states on transition states to reach great behavior on numerous maps.

        Returns
        -------
        The dictionary containing transition states and "q_values" for them.
        """

        compressed_q_table: dict = dict()
        for state in self.q_table.keys():
            compressed_q_table[state.to_transition_state()]: list = list()
        for state in self.q_table.keys():
            compressed_q_table[state.to_transition_state()].append(self.q_table[state])

        for transition_state in compressed_q_table.keys():
            print('\n', transition_state)
            q = np.array(compressed_q_table[transition_state])
            most_popular_actions = np.apply_along_axis(np.argmax, 1, q)
            print(most_popular_actions)
            generalized_q_values = np.bincount(most_popular_actions, minlength=self.env.n_actions)
            compressed_q_table[transition_state] = generalized_q_values
        return compressed_q_table

    def extract_q_table(self, compressed_q_table: dict) -> None:
        """
        Extracts q_table from given compressed q_table and writes the result into agent's field.

        Parameters
        ----------
        compressed_q_table: dict
        """

        for state in tqdm(self.q_table.keys(), file=sys.stdout, desc='Q_table extraction progress'):
            try:
                self.q_table[state] = compressed_q_table[state.to_transition_state()]
            except KeyError:
                self.q_table[state] = [MIN_REWARD] * self.env.n_actions

    @staticmethod
    def load_compressed_q_table_from_file(filename: str) -> dict:
        with open('learning_data\\' + filename, 'rb') as q_file:
            compressed_q_table = pickle.load(q_file)
        return compressed_q_table

    @staticmethod
    def write_compressed_q_table_to_file(filename: str, compressed_q_table: dict) -> None:
        with open('learning_data\\' + filename, 'wb') as q_file:
            pickle.dump(compressed_q_table, q_file)

    def finalize(self) -> None:
        """
        Deletes states which remained unvisited during training process and marks undone actions as the most undesirable.
        """
        states_to_delete = []
        for state in self.q_table.keys():
            if all(map(lambda t: t == 0, self.q_table[state])):
                states_to_delete.append(state)

        for s in states_to_delete:
            self.q_table.pop(s)

        for state in self.q_table.keys():
            for n_a in actions:
                if self.q_table[state][n_a] == 0:
                    self.q_table[state][n_a] = MIN_REWARD
