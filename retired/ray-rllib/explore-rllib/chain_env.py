import gym
from gym import spaces

class ChainEnv(gym.Env):

    def __init__(self, env_config = None):
        env_config = env_config or {}
        self.n = env_config.get("n", 20)
        self.small_reward = env_config.get("small", 2)  # payout for 'backwards' action
        self.large_reward = env_config.get("large", 10)  # payout at end of chain for 'forwards' action
        self.state = 0  # Start at beginning of the chain
        self._horizon = self.n
        self._counter = 0  # For terminating the episode
        self._setup_spaces()

    def _setup_spaces(self):
        ##############
        # TODO: Implement this so that it passes tests
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Discrete(self.n)
        ##############

    def step(self, action):
        assert self.action_space.contains(action)
        if action == 1:  # 'backwards': go back to the beginning, get small reward
            ##############
            # TODO 2: Implement this so that it passes tests
            reward = self.small_reward
            ##############
            self.state = 0
        elif self.state < self.n - 1:  # 'forwards': go up along the chain
            ##############
            # TODO 2: Implement this so that it passes tests
            reward = 0
            self.state += 1
        else:  # 'forwards': stay at the end of the chain, collect large reward
            ##############
            # TODO 2: Implement this so that it passes tests
            reward = self.large_reward
            ##############
        self._counter += 1
        done = self._counter >= self._horizon
        return self.state, reward, done, {}

    def reset(self):
        self.state = 0
        self._counter = 0
        return self.state

if __name__ == '__main__':
    # Tests here:
    from test_exercises import test_chain_env_spaces, test_chain_env_reward

    test_chain_env_spaces(ChainEnv)
    test_chain_env_reward(ChainEnv)
