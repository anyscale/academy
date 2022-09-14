
import logging
import random
import sys
sys.path.append('./')
import tqdm
import argparse
from ray.rllib.offline.json_writer import JsonWriter
import os
from ray import tune

logger = logging.getLogger(__name__)


from rllib_recsim.rllib_recsim import ModifiedLongTermSatisfactionRecSimEnv
from ray.rllib.algorithms.dqn import DQNConfig
from ray.rllib.policy.sample_batch import SampleBatch


def parse_args():
    parser = argparse.ArgumentParser()
    # example results/dqn_recsim_20_v2/DQN/DQN_modified-lts_9e376_00000_0_2022-09-08_14-31-36/checkpoint_000278
    parser.add_argument("--ckpt", type=str)
    parser.add_argument("--seed", type=int, default=100, help="random seed")

    parser.add_argument("--x", type=int, default=0, help="Expert ratio")
    parser.add_argument("--num_episodes", type=int, default=10000, help="Number of episodes to generate")
    parser.add_argument("--output", type=str, default="./data_out")
    return parser.parse_args()

def main(pargs):
    num_candidates = 20
    reward_scale = 1.0

    # use tune to register the environment
    tune.register_env("modified-lts", 
        lambda config: ModifiedLongTermSatisfactionRecSimEnv(config)
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
            "seed": pargs.seed,
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
        .debugging(seed=pargs.seed, log_level="ERROR")
        .training(
            gamma=1.0,
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

    dqn_algo = dqn_config.build()
    checkpoint_path = pargs.ckpt
    if checkpoint_path:
        dqn_algo.restore(checkpoint_path)
    elif pargs.x > 0:
        raise ValueError("Must provide a checkpoint path for expert ratio > 0")


    env = dqn_algo.workers.local_worker().env
    num_episodes = pargs.num_episodes
    episodes = []
    for ep_id in tqdm.tqdm(range(num_episodes)):
        done = False
        time_step = 0
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
            episodes.append(sample_batch)
            obs = next_obs
            time_step += 1

    logger.setLevel(logging.INFO)

    if pargs.x > 0:
        output_name = f"sampled_data_train_random_expert_{pargs.x}_percent_transitions"
    else:
        output_name = f"sampled_data_train_random_transitions_small"

    path = os.path.join(pargs.output, output_name)
    writer = JsonWriter(path)
    for sb in episodes:
        writer.write(sb)


if __name__ == "__main__":
    pargs = parse_args()
    main(pargs)