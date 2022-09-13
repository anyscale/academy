import time
import random
import numpy as np
from pprint import pprint
import matplotlib.pyplot as plt

from ray import tune, air

import recsim 
from rllib_recsim.rllib_recsim import ModifiedLongTermSatisfactionRecSimEnv

# main parameters
seed = 100
num_candidates = 20
reward_scale = 1.0


tune.register_env("modified-lts", 
    lambda config: ModifiedLongTermSatisfactionRecSimEnv(config)
)

from ray.rllib.algorithms.dqn import DQNConfig


env_config_20 = {
    "num_candidates": num_candidates,  
    "slate_size": 1, 
    "resample_documents": True,
    "seed": seed,
    "reward_scale": reward_scale
}

dqn_config = (
    DQNConfig()
    .environment(
        env="modified-lts", 
        env_config=env_config_20,
    )
    .framework("torch")
    .evaluation( # every itartaion run simulation of 100 episodes in parallel
        evaluation_interval=1, 
        evaluation_duration=100, 
        evaluation_duration_unit="episodes",
        evaluation_parallel_to_training=True,
    )
    .rollouts(
        num_rollout_workers=1,
        num_envs_per_worker=1,
        create_env_on_local_worker=True,
        batch_mode="complete_episodes",
    )
    .debugging(seed=seed, log_level="ERROR")
    .training(
        gamma=0.0, # <-------- Make this algorithm bandits-like
        num_atoms=1,
        dueling=False,
        model=dict(
            fcnet_hiddens=[1024, 1024, 1024],
            fcnet_activation='relu',
        ),
        train_batch_size=512,
        lr=3e-4,
        target_network_update_freq=512,
    )
)


tuner = tune.Tuner(
    "DQN",
    param_space=dqn_config.to_dict(),
    run_config=air.RunConfig(
        local_dir='./results/online_rl/bandits_dqn',
        stop={"timesteps_total": 15_000},  # this is enough for it to converge
        checkpoint_config=air.CheckpointConfig(
            checkpoint_frequency=1,
            num_to_keep=1,
        ),
        verbose=1,
    )
)
results = tuner.fit()