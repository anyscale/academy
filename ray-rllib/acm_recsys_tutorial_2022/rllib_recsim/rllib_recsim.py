"""Tools and utils to create RLlib-ready recommender system envs using RecSim.

For examples on how to generate a RecSim env class (usable in RLlib):
See ray.rllib.examples.env.recommender_system_envs_with_recsim.py

For more information on google's RecSim itself:
https://github.com/google-research/recsim
"""

import gym
from typing import Optional

from recsim.simulator import environment, recsim_gym
from recsim.environments import long_term_satisfaction as lts

from ray.rllib.env.env_context import EnvContext

from .wrappers import recsim_gym_wrapper


class ModifiedLTSUserModel(lts.LTSUserModel):

    def __init__(self,
                slate_size,
                user_state_ctor=None,
                response_model_ctor=None,
                seed=0):
        if not response_model_ctor:
            raise TypeError('response_model_ctor is a required callable.')

        user_sampler = ModifiedLTSStaticUserSampler(
            user_ctor=user_state_ctor, seed=seed
        )
        super(lts.LTSUserModel, self).__init__(
            response_model_ctor,
            user_sampler, 
            slate_size
        )


class ModifiedLTSStaticUserSampler(lts.LTSStaticUserSampler):

    def __init__(
        self,
        user_ctor=lts.LTSUserState,
        memory_discount=0.7,
        sensitivity=0.9,
        innovation_stddev=1e-5,
        choc_mean=5.0,
        choc_stddev=0.0,
        kale_mean=0.0,
        kale_stddev=0.0,
        time_budget=10,
        **kwargs
    ):
        super().__init__(
            user_ctor=user_ctor,
            memory_discount=memory_discount,
            sensitivity=sensitivity,
            innovation_stddev=innovation_stddev,
            choc_mean=choc_mean,
            choc_stddev=choc_stddev,
            kale_mean=kale_mean,
            kale_stddev=kale_stddev,
            time_budget=time_budget,
            **kwargs
        )

    def sample_user(self):
        self._state_parameters['net_positive_exposure'] = 1.0
        return self._user_ctor(**self._state_parameters)


class ModifiedLTSDocumentSampler(lts.LTSDocumentSampler):

    def sample_document(self):
        doc_features = {}
        doc_features['doc_id'] = self._doc_count
        if self._doc_count % 2 == 0:
            doc_features['clickbait_score'] = 0.8 + 0.2 * self._rng.random_sample() # sweet
        else:
            doc_features['clickbait_score'] = 0.2 * self._rng.random_sample() # bitter
        self._doc_count += 1
        return self._doc_ctor(**doc_features)

class ModifiedLongTermSatisfactionRecSimEnv(gym.Wrapper):

    """Creates a RLlib-ready gym.Env class given RecSim user and doc models.

    See https://github.com/google-research/recsim for more information on how to
    build the required components from scratch in python using RecSim.
    """

    def __init__(self, config: Optional[EnvContext] = None):

        # Override with default values, in case they are not set by the user.
        default_config = {
            "num_candidates": 20,
            "slate_size": 1,
            "resample_documents": True,
            "seed": 0,
            "convert_to_discrete_action_space": True,
            "wrap_for_bandits": False,
            "reward_scale": 1.0,
        }
        if config is None or isinstance(config, dict):
            config = EnvContext(config or default_config, worker_index=0)
        config.set_defaults(default_config)
        
        reward_aggregator = lts.clicked_engagement_reward
        # Create the RecSim user model instance.
        recsim_user_model = ModifiedLTSUserModel(
            config["slate_size"],
            user_state_ctor=lts.LTSUserState,
            response_model_ctor=lts.LTSResponse,
            seed=config.get("seed", 0),
        )
        # Create the RecSim document sampler instance.
        recsim_document_sampler = ModifiedLTSDocumentSampler(seed=config.get("seed", 0))

        # Create a raw RecSim environment (not yet a gym.Env!).
        raw_recsim_env = environment.SingleUserEnvironment(
            recsim_user_model,
            recsim_document_sampler,
            config["num_candidates"],
            config["slate_size"],
            resample_documents=config["resample_documents"],
        )
        # Convert raw RecSim env to a gym.Env.
        gym_env = recsim_gym.RecSimGymEnv(raw_recsim_env, reward_aggregator)

        # Fix observation space and - if necessary - convert to discrete
        # action space (from multi-discrete).
        env = recsim_gym_wrapper(
            gym_env,
            config["convert_to_discrete_action_space"],
            config["wrap_for_bandits"],
            config["reward_scale"],
        )

        # Call the super (Wrapper constructor) passing it the created env.
        super().__init__(env=env)

    
    def get_user_state(self):
        return self.environment._user_model._user_state.__dict__