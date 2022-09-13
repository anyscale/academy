
from typing import List
import gym
import numpy as np
from gym.spaces import Dict, Discrete, MultiDiscrete, Tuple
from collections import OrderedDict
from ray.rllib.utils.error import UnsupportedSpaceException
from ray.rllib.utils.spaces.space_utils import convert_element_to_space_type

class RecSimObservationSpaceWrapper(gym.ObservationWrapper):
    """Fix RecSim environment's observation space

    In RecSim's observation spaces, the "doc" field is a dictionary keyed by
    document IDs. Those IDs are changing every step, thus generating a
    different observation space in each time. This causes issues for RLlib
    because it expects the observation space to remain the same across steps.

    This environment wrapper fixes that by reindexing the documents by their
    positions in the list.
    """

    def __init__(self, env: gym.Env):
        super().__init__(env)
        obs_space = self.env.observation_space
        doc_space = Dict(
            OrderedDict(
                [
                    (str(k), doc)
                    for k, (_, doc) in enumerate(obs_space["doc"].spaces.items())
                ]
            )
        )
        time_step_space = gym.spaces.Box(-0.5, 0.5, shape=(1, ), dtype=np.float32)
        self.observation_space = Dict(
            OrderedDict(
                [
                    ("user", obs_space["user"]),
                    ("doc", doc_space),
                    ("response", obs_space["response"]),
                    ("time", time_step_space),
                ]
            )
        )
        self._sampled_obs = self.observation_space.sample()
        self.time_step = 0
        self.max_time_step = None
            

    def reset(self, **kwargs):
        self.time_step = 0
        self.max_time_step = self.environment._user_model._user_sampler._state_parameters['time_budget']
        return super().reset(**kwargs)

    def step(self, action):
        self.time_step += 1
        return super().step(action)

    def observation(self, obs):
        new_obs = OrderedDict()
        new_obs["user"] = obs["user"]
        new_obs["doc"] = {str(k): v for k, (_, v) in enumerate(obs["doc"].items())}
        new_obs["response"] = obs["response"]
        new_obs["time"] = np.array([self.time_step], dtype=np.float32) / self.max_time_step - 0.5
        new_obs = convert_element_to_space_type(new_obs, self._sampled_obs)
        return new_obs


class RecSimObservationBanditWrapper(gym.ObservationWrapper):
    """Fix RecSim environment's observation format

    RecSim's observations are keyed by document IDs, and nested under
    "doc" key.
    Our Bandits agent expects the observations to be flat 2D array
    and under "item" key.

    This environment wrapper converts obs into the right format.
    """

    def __init__(self, env: gym.Env):
        super().__init__(env)
        obs_space = self.env.observation_space

        num_items = len(obs_space["doc"])
        embedding_dim = next(iter(obs_space["doc"].values())).shape[-1]
        self.observation_space = Dict(
            OrderedDict(
                [
                    (
                        "item",
                        gym.spaces.Box(
                            low=-1.0, high=1.0, shape=(num_items, embedding_dim)
                        ),
                    ),
                ]
            )
        )
        self._sampled_obs = self.observation_space.sample()

    def observation(self, obs):
        new_obs = OrderedDict()
        new_obs["item"] = np.vstack(list(obs["doc"].values()))
        new_obs = convert_element_to_space_type(new_obs, self._sampled_obs)
        return new_obs

class RecSimRewardScalingWrapper(gym.RewardWrapper):
    """Scale RecSim environment's reward by a given factor

    This environment wrapper scales the reward by a given factor.
    """

    def __init__(self, env: gym.Env, reward_scale: float):
        super().__init__(env)
        self.reward_scale = reward_scale

    def reward(self, reward):
        return self.reward_scale * reward

class RecSimResetWrapper(gym.Wrapper):
    """Fix RecSim environment's reset() and close() function

    RecSim's reset() function returns an observation without the "response"
    field, breaking RLlib's check. This wrapper fixes that by assigning a
    random "response" with engagement hard-coded to -1 which indicates 
    the start of an episode.

    RecSim's close() function raises NotImplementedError. We change the
    behavior to doing nothing.
    """

    def __init__(self, env: gym.Env):
        super().__init__(env)
        self._sampled_obs = self.env.observation_space.sample()
        self.observation_space = Dict(
            OrderedDict(
                [
                    ("user", self.observation_space["user"]),
                    ("doc", self.observation_space["doc"]),
                    ("response", Tuple([
                            Dict(OrderedDict(
                                [
                                ("click", gym.spaces.Discrete(2)),
                                ("engagement", gym.spaces.Box(-1.0, 100, (), np.float32))
                                ]
                            ))
                            for _ in range(self.environment.slate_size)
                        ])
                    ),
                ]
            )
        )


    def reset(self):
        obs = super().reset()
        obs["response"] = self.env.observation_space["response"].sample()
        for i in range(len(obs["response"])):
            obs["response"][i]["engagement"] = -1.0
        obs = convert_element_to_space_type(obs, self._sampled_obs)
        return obs

    def close(self):
        pass


class MultiDiscreteToDiscreteActionWrapper(gym.ActionWrapper):
    """Convert the action space from MultiDiscrete to Discrete

    At this moment, RLlib's DQN algorithms only work on Discrete action space.
    This wrapper allows us to apply DQN algorithms to the RecSim environment.
    """

    def __init__(self, env: gym.Env):
        super().__init__(env)

        if not isinstance(env.action_space, MultiDiscrete):
            raise UnsupportedSpaceException(
                f"Action space {env.action_space} "
                f"is not supported by {self.__class__.__name__}"
            )
        self.action_space_dimensions = env.action_space.nvec
        self.action_space = Discrete(np.prod(self.action_space_dimensions))

    def action(self, action: int) -> List[int]:
        """Convert a Discrete action to a MultiDiscrete action"""
        multi_action = [None] * len(self.action_space_dimensions)
        for idx, n in enumerate(self.action_space_dimensions):
            action, dim_action = divmod(action, n)
            multi_action[idx] = dim_action
        return multi_action


def recsim_gym_wrapper(
    recsim_gym_env: gym.Env,
    convert_to_discrete_action_space: bool = False,
    wrap_for_bandits: bool = False,
    reward_scale: float = -1,
) -> gym.Env:
    """Makes sure a RecSim gym.Env can ba handled by RLlib.

    In RecSim's observation spaces, the "doc" field is a dictionary keyed by
    document IDs. Those IDs are changing every step, thus generating a
    different observation space in each time. This causes issues for RLlib
    because it expects the observation space to remain the same across steps.

    Also, RecSim's reset() function returns an observation without the
    "response" field, breaking RLlib's check. This wrapper fixes that by
    assigning a random "response".

    Args:
        recsim_gym_env: The RecSim gym.Env instance. Usually resulting from a
            raw RecSim env having been passed through RecSim's utility function:
            `recsim.simulator.recsim_gym.RecSimGymEnv()`.
        convert_to_discrete_action_space: Optional bool indicating, whether
            the action space of the created env class should be Discrete
            (rather than MultiDiscrete, even if slate size > 1). This is useful
            for algorithms that don't support MultiDiscrete action spaces,
            such as RLlib's DQN. If None, `convert_to_discrete_action_space`
            may also be provided via the EnvContext (config) when creating an
            actual env instance.
        wrap_for_bandits: Bool indicating, whether this RecSim env should be
            wrapped for use with our Bandits agent.

    Returns:
        An RLlib-ready gym.Env instance.
    """
    env = RecSimResetWrapper(recsim_gym_env)
    env = RecSimObservationSpaceWrapper(env)
    if convert_to_discrete_action_space:
        env = MultiDiscreteToDiscreteActionWrapper(env)
    if wrap_for_bandits:
        env = RecSimObservationBanditWrapper(env)
    if reward_scale != -1:
        env = RecSimRewardScalingWrapper(env, reward_scale)
    return env