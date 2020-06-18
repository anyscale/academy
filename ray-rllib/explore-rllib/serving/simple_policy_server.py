import argparse, os

import gym
from gym import spaces
import numpy as np

import ray
from ray.rllib.agents.dqn.dqn import DQNTrainer
from ray.rllib.agents.pg.pg import PGTrainer
from ray.rllib.env.external_env import ExternalEnv
# from ray.rllib.utils.policy_server import PolicyServer
from ray.rllib.env.policy_server_input import PolicyServerInput
from ray.tune.logger import pretty_print
from ray.tune.registry import register_env

SERVER_ADDRESS = "localhost"
SERVER_PORT = 8900

parser = argparse.ArgumentParser()
parser.add_argument("--address", type=str, required=False,
    help="The Ray cluster address to use. If omitted, a local, one-node Ray cluster is started.")
parser.add_argument("--action-size", type=int, required=True,
    help="The number of actions, which is equivalent to the number of arms, so one action per arm that you can pull.")
parser.add_argument("--observation-size", type=int, required=True,
    help="The number of possible observations when an action is taken.")
parser.add_argument("--checkpoint-file", type=str, required=True)
parser.add_argument("--run", type=str, required=True)


class SimpleServing(ExternalEnv):
    def __init__(self, config):
        ExternalEnv.__init__(
            self, spaces.Discrete(config["action_size"]),
            spaces.Box(
                low=-10, high=10,
                shape=(config["observation_size"],),
                dtype=np.float32))
        self.server = config["input"]

    def run(self):
        print("Starting policy server at {}:{}".format(SERVER_ADDRESS,
                                                       SERVER_PORT))
        # TODO: PolicyServer is deprecated. Switch to rllib.env.PolicyServerInput
        # server = PolicyServer(self, SERVER_ADDRESS, SERVER_PORT)
        self.server.serve_forever()


if __name__ == "__main__":
    args = parser.parse_args()
    if args.address:
        ray.init(address=args.address)
    else:
        ray.init()

    # Register our custom SimpleServing environment as a known environment
    # with name "srv".
    register_env("srv", lambda config: SimpleServing(config))

    if args.run == "DQN":
        agent = DQNTrainer(
            env="srv",
            config={
                # Use a single process to avoid needing a load balancer
                "num_workers": 0,
                # Configure the agent to run short iterations for debugging
                #"exploration_fraction": 0.01,
                "learning_starts": 100,
                "timesteps_per_iteration": 200,
                "env_config": {
                    # Use the connector server to generate experiences.
                    "input": (
                        lambda ioctx: PolicyServerInput(ioctx, SERVER_ADDRESS, SERVER_PORT)
                    ),
                    "observation_size": args.observation_size,
                    "action_size": args.action_size,
                },
            })
    elif args.run == "PG":
        agent = PGTrainer(
            env="srv",
            config={
                "num_workers": 0,
                "env_config": {
                    # Use the connector server to generate experiences.
                    "input": (
                        lambda ioctx: PolicyServerInput(ioctx, SERVER_ADDRESS, SERVER_PORT)
                    ),
                    "observation_size": args.observation_size,
                    "action_size": args.action_size,
                },
            })
    else:
        raise ValueError("--run must be DQN or PG")

    # Attempt to restore from checkpoint if possible.
    if os.path.exists(args.checkpoint_file):
        checkpoint_file = open(args.checkpoint_file).read()
        print("Restoring from checkpoint path", checkpoint_file)
        agent.restore(checkpoint_file)

    # Serving and training loop
    while True:
        print(pretty_print(agent.train()))
        checkpoint_file = agent.save()
        print("Last checkpoint", checkpoint_file)
        with open(args.checkpoint_file, "w") as f:
            f.write(checkpoint_file)
