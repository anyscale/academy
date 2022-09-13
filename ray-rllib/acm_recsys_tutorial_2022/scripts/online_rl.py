from asyncio.log import logger
from pprint import pprint
import random
import numpy as np
import sys
sys.path.append('./')
from demo_recsys.recsim.rllib_recsim import LongTermSatisfactionRecSimEnv
import gym

import matplotlib.pyplot as plt
import time
from ray import tune
# from ray.air.callbacks.wandb import WandbLoggerCallback
# from ray.tune.logger import DEFAULT_LOGGERS



import ray
# ray.init(local_mode=True)
seed = 100
num_candidates = 20
reward_scale = 1.0
# wandb_logger = WandbLoggerCallback(
#     project="recsim",
#     api_key_file="~/.wandb_key",
#     log_config=True,
# )


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
######################
### Getting baseline numbers
######################

# """
# Function that measures and outputs the random baseline reward.
# This is the expected accumulated reward per episode, if we act randomly (recommend random items) at each time step.
def calc_baseline(baseline_type="random",
                  episodes=100, threshold=0.5, verbose=False):

    env_config = {
        # The number of possible documents/videos/candidates that we can recommend
        # no flattening necessary (see `convert_to_discrete_action_space=False` below)
        "num_candidates": num_candidates,  
        # The number of recommendations that we will be making
        "slate_size": 1,  # MultiDiscrete([20]) -> Discrete(20)
        # Set to False for re-using the same candidate documents each timestep.
        "resample_documents": True,
        # # Convert MultiDiscrete actions to Discrete (flatten action space).
        "convert_to_discrete_action_space": False,
        # # Wrap observations for RLlib bandit: Only changes dict keys ("item" instead of "doc").
        "wrap_for_bandits": False,
        # Use consistent seeds for the environment ...
        "seed": seed,
        "reward_scale": reward_scale,
    }

    env = LTSWithStrongerDissatisfactionEffect(
        LongTermSatisfactionRecSimEnv(env_config))
    # Reset the env.
    obs = env.reset()

    # Number of episodes already done.
    num_episodes = 0
    # Current episode's accumulated reward.
    episode_reward = 0.0
    epsiode_satisfaction = []
    # Collect all episode rewards here to be able to calculate a random baseline reward.
    episode_rewards = []
    episode_satisfactions = []
    
    # Enter while loop (to step through the episode).
    time_step = 0
    while num_episodes < episodes:
        # Produce an action
        action_dict = {
            'argmax': int(max(obs['doc'], key=lambda x: obs['doc'][x])), # greedy choc
            'argmin': int(min(obs['doc'], key=lambda x: obs['doc'][x])), # greedy kale
            'random': env.action_space.sample().item(),
        }
        action_dict['random_extremes'] = action_dict[
            'argmax' if random.random() < threshold else 'argmin'
        ]
        action_dict["2-1-2"] = action_dict["argmin"] if time_step % 2 == 0 else action_dict["argmax"]
        action = action_dict[baseline_type]
        
        # Send the action to the env's `step()` method to receive: obs, reward, done, and info.
        obs, reward, done, _ = env.step([action])
        episode_reward += reward
        epsiode_satisfaction.append(env.environment._user_model._user_state.satisfaction)

        time_step += 1
        # Check, whether the episde is done, if yes, reset and increase episode counter.
        if done:
            if verbose:
                print(f"Episode done - accumulated reward={episode_reward}")
            elif num_episodes % 99 == 0:
                print(f" {num_episodes} ", end="")
            elif num_episodes % 9 == 0:
                print(".", end="")
                
            # increment on end of episode
            num_episodes += 1
            time_step = 0
            obs = env.reset()
            episode_rewards.append(episode_reward)
            episode_reward = 0.0
            episode_satisfactions.append(np.mean(epsiode_satisfaction))

    # Print out and return mean episode reward (and standard error of the mean).
    env_mean_reward = np.mean(episode_rewards)
    env_sd_reward = np.std(episode_rewards)

    # Print out the satisfaction over the episodes
    env_mean_satisfaction = np.mean(episode_satisfactions)
    env_sd_satisfaction = np.std(episode_satisfactions)
    
    print(f"\nMean {baseline_type} baseline reward: {env_mean_reward:.2f}+/-{env_sd_reward:.2f}, satisfaction: {env_mean_satisfaction:.2f}+/-{env_sd_satisfaction:.2f}")

    return env_mean_reward, episode_rewards

start_time = time.time()
num_episodes=1000
calc_baseline(baseline_type="argmin", episodes=num_episodes)
calc_baseline(baseline_type="argmax", episodes=num_episodes)
calc_baseline(baseline_type="random", episodes=num_episodes)
calc_baseline(baseline_type="random_extremes", episodes=num_episodes, threshold=0.5)
calc_baseline(baseline_type="2-1-2", episodes=num_episodes)

print(f"Environment by itself took {time.time() - start_time:.2f} seconds")


######################
### Trying Bandits
######################

"""
from ray.rllib.algorithms.bandit import BanditLinUCBConfig

tune.register_env("modified-lts", 
    lambda config: LTSWithStrongerDissatisfactionEffect(
        LongTermSatisfactionRecSimEnv(config))
)

bandit_config = BanditLinUCBConfig()
# Setup our config object to use our environment
env_config_20 = \
    {
        # The number of possible documents/videos/candidates that we can recommend
        "num_candidates": 20,  
        # The number of recommendations that we will be making
        "slate_size": 1,  # MultiDiscrete([20]) -> Discrete(20)
        # Set to False for re-using the same candidate doecuments each timestep.
        "resample_documents": True,
        # Convert MultiDiscrete actions to Discrete (flatten action space).
        "convert_to_discrete_action_space": True,
        # Wrap observations for RLlib bandit: Only changes dict keys ("item" instead of "doc").
        "wrap_for_bandits": True,
        # Use consistent seeds for the environment ...
        "seed": 0
    }

# Set it up for the correct environment:
bandit_config.environment(env="modified-lts", env_config=env_config_20)

# Decide if you want torch or tensorflow DL framework.  Default is "tf"
bandit_config.framework("torch")

# Setup evaluation
# Explicitly set "explore"=False to override default
bandit_config.evaluation(
    evaluation_interval=10, 
    evaluation_duration=20, 
    evaluation_duration_unit="timesteps",
    # evaluation_config = {"explore" : False})
)

# Setup sampling rollout workers
# +1 for head node, num parallel workers or actors for rollouts
bandit_config.rollouts(
    num_rollout_workers=1,
    num_envs_per_worker=1,
    # enable_connectors=True)
)


# Set the log level to DEBUG, INFO, WARN, or ERROR 
# seed the algorithm / policy
bandit_config.debugging(seed=0, log_level="ERROR")

# for increasing logging frequency in the terminal for this tutorial
bandit_config.reporting(
    min_train_timesteps_per_iteration=1,
    metrics_num_episodes_for_smoothing=2) #200

start_time = time.time()

# Use the config object's `build()` method for generating
# an RLlib Algorithm instance that we can then train.
linucb_algo = bandit_config.build()
print(f"Algorithm type: {type(linucb_algo)}")

# train the Algorithm instance for 100 iterations
num_iterations = 100
rewards = []
checkpoint_dir = "./results/bandit_recsim/"

train_algo_and_eval(linucb_algo, num_iterations, checkpoint_dir)
# """


######################
### Trying DQN with gamma = 0 -- Bandit
######################

# """

from ray.rllib.algorithms.dqn import DQNConfig

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

from ray import air

tuner = tune.Tuner(
    "DQN",
    param_space=dqn_config.to_dict(),
    run_config=air.RunConfig(
        local_dir=checkpoint_dir,
        stop={"timesteps_total": 1_000_000},
        checkpoint_config=air.CheckpointConfig(
            checkpoint_frequency=1,
            num_to_keep=1,
            checkpoint_score_attribute="episode_reward_mean",
        )
    )
)
results = tuner.fit()


# dqn_algo.restore("results/dqn_recsim_20_v2/DQN/DQN_modified-lts_bdf54_00000_0_2022-09-07_10-15-59/params.pkl")
# breakpoint()


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