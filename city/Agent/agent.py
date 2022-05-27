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
        self.q_table: dict[State, dict[int, int]] = \
            {state: [0 for _ in range(len(actions))] for state in self.env.states}

    def learn(self, n_episodes: int = 100, alpha: float = 0.7, gamma: float = 0.7, epsilon: float = 0.8) -> None:
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
