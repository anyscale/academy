import argparse

import ray
from ray import tune, air
from ray.rllib.algorithms.dqn import DQNConfig

import sys 
sys.path.append('./')
from rllib_recsim.rllib_recsim import ModifiedLongTermSatisfactionRecSimEnv


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=100, help="random seed")
    parser.add_argument(
        "--num_candidates", type=int, default=20, help="Number of candidates"
    )
    parser.add_argument("--gamma", type=float, default=0.99, help="discount factor")
    parser.add_argument("--exp_name", type=str, help="optional experiment name")
    parser.add_argument(
        "--timesteps", type=int, default=20_000, help="Number of timesteps for training"
    )
    parser.add_argument("--num_workers", type=int, default=1, help="Number of workers")
    parser.add_argument("--batch_size", type=int, default=1024, help="train batch size")
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

    exp_name = pargs.exp_name or f"gamma_{pargs.gamma}"


    # set up the environment config
    env_config = {
        "num_candidates": pargs.num_candidates,  
        "slate_size": 1, 
        "resample_documents": True,
        "seed": pargs.seed,
        "reward_scale": 1.0
    }


    # setup the config for the DQN agent
    config = (
        DQNConfig()
        .environment(
            env="modified-lts", 
            env_config=env_config,
        )
        .framework("torch")
        .evaluation( # every itartaion run simulation of 100 episodes in parallel
            evaluation_interval=1, 
            evaluation_duration=100, 
            evaluation_duration_unit="episodes",
            evaluation_parallel_to_training=True,
        )
        .rollouts(
            num_rollout_workers=pargs.num_workers,
            num_envs_per_worker=1,
            create_env_on_local_worker=True,
            batch_mode="complete_episodes",
        )
        .debugging(seed=pargs.seed, log_level="ERROR")
        .training(
            gamma=pargs.gamma, # <-------- Make this algorithm bandits-like
            num_atoms=1,
            dueling=False,
            model=dict(
                fcnet_hiddens=[1024, 1024, 1024],
                fcnet_activation='relu',
            ),
            train_batch_size=pargs.batch_size,
            lr=pargs.lr,
            target_network_update_freq=pargs.batch_size,
        )
    )

    tuner = tune.Tuner(
        "DQN",
        param_space=config.to_dict(),
        run_config=air.RunConfig(
            local_dir=f'./results_scripts/online_rl',
            stop={"timesteps_total": pargs.timesteps},
            checkpoint_config=air.CheckpointConfig(
                checkpoint_frequency=1,
                num_to_keep=1,
            ),
            name=exp_name
        )
    )
    tuner.fit()


if __name__ == "__main__":
    main(parse_args())