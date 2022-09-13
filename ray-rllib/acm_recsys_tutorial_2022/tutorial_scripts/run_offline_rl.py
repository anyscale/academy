
import sys
sys.path.append('./')
from rllib_recsim.rllib_recsim import ModifiedLongTermSatisfactionRecSimEnv
from ray import air, tune
import gym

import ray
import argparse
from ray.rllib.algorithms.dqn import DQNConfig

VALID_SUFFIXES = [
    "sampled_data_train_random_expert_1_percent_transitions",
    "sampled_data_train_random_expert_5_percent_transitions",
    "sampled_data_train_random_expert_10_percent_transitions",
    "sampled_data_train_random_expert_20_percent_transitions",
    "sampled_data_train_random_transitions",
]

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=100, help="random seed")
    parser.add_argument("--dataset_suffix", type=str, default="train", help="The dataset suffix used in the s3 bucket.")
    parser.add_argument("--run_ope", action='store_true', help="run evaluation on validation dataset")
    parser.add_argument(
        "--num_candidates", type=int, default=20, help="Number of candidates"
    )
    parser.add_argument("--gamma", type=float, default=1.0, help="discount factor")
    parser.add_argument("--exp_name", type=str, help="optional experiment name")
    parser.add_argument(
        "--timesteps", type=int, default=20_000, help="Number of timesteps for training"
    )
    parser.add_argument("--num_workers", type=int, default=1, help="Number of workers")
    parser.add_argument("--batch_size", type=int, default=512, help="train batch size")
    parser.add_argument("--lr", type=float, default=3e-4, help="learning rate")
    parser.add_argument(
        "--local_mode", action='store_true', default=False, help="Whether to run in local mode"
    )

    return parser.parse_args()



def main(pargs):
    if pargs.local_mode:
        ray.init(local_mode=True)
    
    # use tune to register the environment
    tune.register_env("modified-lts", 
        lambda config: ModifiedLongTermSatisfactionRecSimEnv(config)
    )

    if pargs.dataset_suffix not in VALID_SUFFIXES:
        raise ValueError(f"Invalid dataset suffix: {pargs.dataset_suffix}. Must be one of {VALID_SUFFIXES}")

    # set up the environment config
    env_config = {
        "num_candidates": pargs.num_candidates,  
        "slate_size": 1, 
        "resample_documents": True,
        "seed": pargs.seed,
        "reward_scale": 1.0
    }

    env = ModifiedLongTermSatisfactionRecSimEnv(env_config)


    action_space = env.action_space
    observation_space = env.observation_space

    prefix = "s3://air-example-data/rllib/acm_recsys22_tutorial_data/"
    train_data_path = prefix + pargs.dataset_suffix

    dqn_config = (
        DQNConfig()
        .offline_data(
            input_='dataset',
            input_config={
                'format': 'json',
                'paths': train_data_path
            }
        )
        .environment(
            action_space=action_space,
            observation_space=observation_space,
        )
        .framework("torch")
        
        .rollouts(
            num_rollout_workers=1,
            num_envs_per_worker=1,
            create_env_on_local_worker=True,
            batch_mode="complete_episodes",
        )
        .debugging(seed=pargs.seed, log_level="ERROR")
        .training(
            gamma=1.0,
            num_atoms=1,
            double_q=True,
            dueling=False, 
            model=dict(
                fcnet_hiddens=[1024, 1024, 1024],
                fcnet_activation='relu', 
            ),
            train_batch_size=512,
            lr=3e-4, 
            target_network_update_freq=512,
            replay_buffer_config={
                "capacity": 512,
                "learning_starts": 0
            }
        )
        .reporting(
            min_time_s_per_iteration=0,
            min_train_timesteps_per_iteration=0,
            min_sample_timesteps_per_iteration=0
        )
    )

    if pargs.run_ope:
        from ray.rllib.offline.estimators import (
            ImportanceSampling, WeightedImportanceSampling
        )

        valid_data_path = prefix + "sampled_data_valid_random_1k_v1"
        dqn_config = (
            dqn_config
            .evaluation(
                evaluation_interval=10, 
                evaluation_duration=1000, 
                evaluation_duration_unit="episodes",
                evaluation_parallel_to_training=True,
                evaluation_config={
                    "input": "dataset",
                    "input_config": {
                        "format": "json",
                        "paths": valid_data_path
                    },
                    "train_batch_size": 1 # my returned batch should have at least 1 timestep (which is true if you sample more > 1 episodes.) If this is not specified the default train_batch_size number of timesteps will be sampled, ignoring evaluation duration defined above.
                },
                off_policy_estimation_methods={
                    "is": {"type": ImportanceSampling},
                    "wis": {"type": WeightedImportanceSampling},
                }
            )
        )
    else:
        dqn_config = (
            dqn_config
            .evaluation(
                evaluation_interval=1, 
                evaluation_duration=10, 
                evaluation_duration_unit="episodes",
                evaluation_parallel_to_training=True,
                evaluation_config={
                    "input": "sampler",
                    "explore": False,
                    "env": "modified-lts",
                    "env_config": env_config,
                },
            )
        )


    
    tuner = tune.Tuner(
        "DQN",
        param_space=dqn_config.to_dict(),
        run_config=air.RunConfig(
            local_dir=f"./results_scripts/offline_rl/{pargs.dataset_suffix}",
            stop={"timesteps_total": 1_000_000},
            checkpoint_config=air.CheckpointConfig(
                checkpoint_frequency=1,
                num_to_keep=1,
            )
        )
    )
    tuner.fit()


if __name__ == "__main__":
    pargs = parse_args()
    main(pargs)

