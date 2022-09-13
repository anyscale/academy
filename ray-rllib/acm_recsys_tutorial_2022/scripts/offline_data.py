from asyncio.log import logger
from asyncore import write
import logging
from pprint import pprint
import random
import numpy as np
import sys
sys.path.append('./')
from demo_recsys.recsim.rllib_recsim import LongTermSatisfactionRecSimEnv
import gym
import tqdm

import matplotlib.pyplot as plt
import time
from ray import tune
# from ray.air.callbacks.wandb import WandbLoggerCallback
# from ray.tune.logger import DEFAULT_LOGGERS
import random


import ray
seed = 50
num_candidates = 20
reward_scale = 1.0
# wandb_logger = WandbLoggerCallback(
#     project="recsim",
#     api_key_file="~/.wandb_key",
#     log_config=True,
# )

from ray.rllib.evaluation.collectors.agent_collector import AgentCollector
from ray.rllib.evaluation.sampler import _env_runner
from ray.rllib.algorithms import Algorithm
import ray.rllib.offline.dataset_reader 


class LTSWithStrongerDissatisfactionEffect(gym.Wrapper):

    def __init__(self, env):
        # Tweak incoming environment.
        env.environment._user_model._user_sampler._state_parameters.update({
            "memory_discount": 0.7,
            "sensitivity": 0.9,
            "innovation_stddev": 1e-5,
            "choc_mean": 5.0,
            "choc_stddev": 0.0,
            "kale_mean": 0.0,
            "kale_stddev": 0.0,            
            "time_budget": 10,
        })
        # env.environment._user_model._user_sampler._state_parameters.update({
        #     # "memory_discount": 0.7,
        #     "sensitivity": 0.058,
        #     # "innovation_stddev": 1e-5,
        #     # "choc_mean": 5.0,
        #     "choc_stddev": 0.1,
        #     # "kale_mean": 0.0,
        #     "kale_stddev": 0.1,            
        #     "time_budget": 120,
        # })

        super().__init__(env)

######################
### Playing with env
######################
"""
Show that greedy kale is a good initial strategy for this user profile.
Show that greedy chocolate is not as good but the immediate reward is substantially higher. 
With this kind of env random could result in a better baseline. We try it but it is still not better than kale. 
So what is better than kale?
We sweep threshold over random extremes and find that 0.3 is somewhat better than greedy kale. 
So now the question is how do we learn the optimal strategy without knowing anything about the dynamics of the user?
Bandits? 
DQN?
"""

"""
config = {
    'slate_size': 1,
    'resample_documents': False,
    'seed': 0,
}
env = LongTermSatisfactionRecSimEnv(config)
env = LTSWithStrongerDissatisfactionEffect(env)
pprint(env.environment._user_model._user_sampler._state_parameters)

num_episodes = 1
# baseline = 'random_extremes'
baseline = 'random'
rewards_list = []
# for threshold in np.arange(0.0, 1.1, 0.1):
for ep_id in range(num_episodes):
    done = False
    ep_rewards = []
    ep_npes, ep_satisfactions = [], []
    obs = env.reset()
    # pprint(env.environment._user_model._user_sampler._state_parameters)
    env_user_state = env.environment._user_model._user_state
    ep_npes.append(env_user_state.net_positive_exposure)
    ep_satisfactions.append(env_user_state.satisfaction)
    while not done:
        action_dict = {
            'argmax': int(max(obs['doc'], key=lambda x: obs['doc'][x])), # greedy choc
            'argmin': int(min(obs['doc'], key=lambda x: obs['doc'][x])), # greedy kale
            'random': env.action_space.sample().item(),
        }
        action_dict['random_extremes'] = action_dict[
            'argmax' if random.random() < 1.0 else 'argmin'
        ]

        action = action_dict[baseline]

        # print('action = ', action)

        obs, reward, done, info = env.step([action])
        ep_rewards.append(reward)
        env_user_state = env.environment._user_model._user_state
        ep_npes.append(env_user_state.net_positive_exposure)
        ep_satisfactions.append(env_user_state.satisfaction)

    rewards_list.append(ep_rewards)
# print('threshold = ', threshold)
print('reward_total = ', np.mean(np.sum(np.array(rewards_list), -1)).item())

plt.figure()
plt.plot(ep_npes)
plt.title('Net Positive Exposure')

plt.figure()
plt.plot(ep_satisfactions)
plt.title('Satisfaction')

plt.figure()
plt.plot(ep_rewards)
plt.title('Rewards')

plt.show()
breakpoint()

# """

# """

from ray.rllib.algorithms.dqn import DQNConfig, DQN
from ray.rllib.policy.sample_batch import SampleBatch, concat_samples
from ray.rllib.evaluation.sample_batch_builder import SampleBatchBuilder

tune.register_env("modified-lts", 
    lambda config: LTSWithStrongerDissatisfactionEffect(
        LongTermSatisfactionRecSimEnv(config))
)


env_config_20 = \
    {
        # The number of possible documents/videos/candidates that we can recommend
        "num_candidates": num_candidates,  
        # The number of recommendations that we will be making
        "slate_size": 1,  # MultiDiscrete([20]) -> Discrete(20)
        # Set to False for re-using the same candidate doecuments each timestep.
        "resample_documents": True,
        # Convert MultiDiscrete actions to Discrete (flatten action space).
        "convert_to_discrete_action_space": True,
        # Wrap observations for RLlib bandit: Only changes dict keys ("item" instead of "doc").
        "wrap_for_bandits": False,
        # Use consistent seeds for the environment ...
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
    .evaluation(
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
        gamma=1.0,
        num_atoms=1,
        dueling=False, #tune.grid_search([False, True]),
        model=dict(
            fcnet_hiddens=[1024, 1024, 1024], #tune.grid_search([[32, 32], [64, 64], [128, 128, 128]]),
            fcnet_activation='relu', #tune.grid_search(['relu', 'tanh']), #can use "tanh" or "relu",
        ),
        train_batch_size=512, #tune.grid_search([32, 512, 1024]),
        lr=3e-4, #tune.grid_search([1e-4, 3e-4, 3e-3]),
        target_network_update_freq=512,
    )
)

dqn_algo = dqn_config.build()
checkpoint_dir = "./results/dqn_recsim_20_v2/"
num_iterations = 100
print("Algorithm DQN")

# from ray import air


# tuner = tune.Tuner(
#     "DQN",
#     param_space=dqn_config.to_dict(),
#     run_config=air.RunConfig(
#         local_dir=checkpoint_dir,
#         stop={"timesteps_total": 1_000_000},
#         checkpoint_config=air.CheckpointConfig(
#             checkpoint_frequency=1,
#             num_to_keep=2,
#             checkpoint_score_attribute="evaluation/episode_reward_mean",
#         )
#     )
# )
# results = tuner.fit()
# checkpoint_path = "results/dqn_recsim_20_v2/DQN/DQN_modified-lts_792ba_00000_0_2022-09-07_11-11-20/checkpoint_000031"
checkpoint_path = "results/dqn_recsim_20_v2/DQN/DQN_modified-lts_9e376_00000_0_2022-09-08_14-31-36/checkpoint_000278"
dqn_algo.restore(checkpoint_path)


env = dqn_algo.workers.local_worker().env
num_episodes = 10000
episodes = []
for ep_id in tqdm.tqdm(range(num_episodes)):
    done = False
    time_step = 0
    episode_data = []
    builder = SampleBatchBuilder()
    obs = env.reset()
    if random.random() < 0.2:
        mode = 'expert'
    else:
        mode = 'random'
    while not done:
        if mode == 'expert':
            action = dqn_algo.compute_action(obs)
        else:
            action = env.action_space.sample()
        next_obs, reward, done, info = env.step(action)
        sample_batch = SampleBatch({
            SampleBatch.CUR_OBS: [obs],
            SampleBatch.NEXT_OBS: [next_obs],
            SampleBatch.ACTIONS: [action],
            SampleBatch.REWARDS: [reward],
            SampleBatch.DONES: [done],
            SampleBatch.EPS_ID: [ep_id],
            SampleBatch.T: [time_step],
            SampleBatch.ACTION_PROB: [1/num_candidates],
        })
        # builder.add_batch(sample_batch)
        episodes.append(sample_batch)
        obs = next_obs
        time_step += 1

    # episode = builder.build_and_reset()
    # episodes.append(episode)

from ray.rllib.offline.json_writer import JsonWriter
import os

logger.setLevel(logging.INFO)

path = os.path.join("demo_recsys", "data", "sampled_data_train_random_expert_20_percent_transitions")
writer = JsonWriter(path)
for sb in episodes:
    writer.write(sb)

# """

######################
### Trying PPO
######################
"""
from ray.rllib.agents.ppo import PPOConfig

tune.register_env("modified-lts", 
    lambda config: LTSWithStrongerDissatisfactionEffect(
        LongTermSatisfactionRecSimEnv(config))
)


env_config_20 = \
    {
        # The number of possible documents/videos/candidates that we can recommend
        "num_candidates": num_candidates,  
        # The number of recommendations that we will be making
        "slate_size": 1,  # MultiDiscrete([20]) -> Discrete(20)
        # Set to False for re-using the same candidate doecuments each timestep.
        "resample_documents": True,
        # Convert MultiDiscrete actions to Discrete (flatten action space).
        "convert_to_discrete_action_space": True,
        # Wrap observations for RLlib bandit: Only changes dict keys ("item" instead of "doc").
        "wrap_for_bandits": False,
        # Use consistent seeds for the environment ...
        "seed": seed,
        "reward_scale": reward_scale,
    }


ppo_config = (
    PPOConfig()
    .environment(
        env="modified-lts", 
        env_config=env_config_20,
        # clip_rewards=True,
    )
    .framework("torch")
    .evaluation(
        evaluation_interval=10, 
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
        gamma=0.0,
        # lambda_=0.95,
        # kl_coeff=0.5,
        # clip_param=0.1,
        # vf_clip_param=10.0,
        # entropy_coeff=0.01,
        train_batch_size=2048,
        sgd_minibatch_size=512,
        num_sgd_iter=1,
        model=dict(
            fcnet_hiddens=[1024, 1024, 1024], #tune.grid_search([[32, 32], [64, 64], [128, 128, 128]]),
            fcnet_activation='relu', #tune.grid_search(['relu', 'tanh']), #can use "tanh" or "relu",
            # use_lstm=True,
            # max_seq_len=4,
            # lstm_use_prev_reward=True,
            # lstm_use_prev_action=True,
        ),
        lr=1e-4, #tune.grid_search([1e-4, 3e-4, 3e-3]),
    )
)

num_iterations = 100
checkpoint_dir = "./results/ppo_recsim_20/"
print("Algorithm PPO")


# train_algo_and_eval(dqn_algo, num_iterations, checkpoint_dir)
tune.run(
    "PPO",
    config=ppo_config.to_dict(),
    local_dir=checkpoint_dir,
    stop={"timesteps_total": 10000000},
    verbose=3,
    # callbacks=[wandb_logger]
)

# """

"""
######################
### Trying SlateQ
######################

from ray.rllib.agents.slateq import SlateQConfig

tune.register_env("modified-lts", 
    lambda config: LTSWithStrongerDissatisfactionEffect(
        LongTermSatisfactionRecSimEnv(config))
)


env_config_20 = \
    {
        # The number of possible documents/videos/candidates that we can recommend
        "num_candidates": num_candidates,  
        # The number of recommendations that we will be making
        "slate_size": 1,  # MultiDiscrete([20]) -> Discrete(20)
        # Set to False for re-using the same candidate doecuments each timestep.
        "resample_documents": True,
        # Convert MultiDiscrete actions to Discrete (flatten action space).
        "convert_to_discrete_action_space": False,
        # Wrap observations for RLlib bandit: Only changes dict keys ("item" instead of "doc").
        # "wrap_for_bandits": False,
        # Use consistent seeds for the environment ...
        "seed": seed
        
    }


ppo_config = (
    SlateQConfig()
    .environment(
        env="modified-lts", 
        env_config=env_config_20,
        clip_rewards=True,
    )
    .framework("torch")
    .evaluation(
        evaluation_interval=10, 
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
        gamma=0.99,
        model=dict(
            fcnet_hiddens=[1024, 1024, 1024], #tune.grid_search([[32, 32], [64, 64], [128, 128, 128]]),
            fcnet_activation='relu', #tune.grid_search(['relu', 'tanh']), #can use "tanh" or "relu",
            # use_lstm=True,
            # max_seq_len=4,
            # lstm_use_prev_reward=True,
            # vf_share_layers=True,
        ),
        target_network_update_freq=3200,
        # lr=3e-4, #tune.grid_search([1e-4, 3e-4, 3e-3]),
    )
)

# dqn_algo = dqn_config.build()

num_iterations = 100
checkpoint_dir = "./results/slateq_recsim_20/"
print("Algorithm SlateQ")

# train_algo_and_eval(dqn_algo, num_iterations, checkpoint_dir)
tune.run(
    "SlateQ",
    config=ppo_config.to_dict(),
    local_dir=checkpoint_dir,
    stop={"timesteps_total": 10000000},
    verbose=3,
)

# """