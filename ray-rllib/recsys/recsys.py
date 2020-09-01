#!/usr/bin/env python
# encoding: utf-8

from argparse import ArgumentParser
from collections import defaultdict
from gym import spaces
from gym.utils import seeding
from paretoset import paretoset
from pathlib import Path
from ray.tune.registry import register_env
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from tqdm import tqdm
import csv
import gym
import numpy as np
import os
import pandas as pd
import pdb
import random
import ray
import ray.rllib.agents.ppo as ppo
import shutil
import sys
import traceback
import warnings


######################################################################
## Gym environment

class JokeRec (gym.Env):
    metadata = {
        "render.modes": ["human"]
        }

    DENSE_SUBMATRIX = [ 5, 7, 8, 13, 15, 16, 17, 18, 19, 20 ]
    ROW_LENGTH = 100
    MAX_STEPS = ROW_LENGTH - len(DENSE_SUBMATRIX)

    NO_RATING = "99"
    MAX_RATING = 10.0

    REWARD_UNRATED = -0.05	# item was not rated
    REWARD_DEPLETED = -0.1	# items depleted


    def __init__ (self, config):
        # NB: here we're passing strings via config; RLlib use of JSON
        # parser was throwing exceptions due to config values
        self.dense = eval(config["dense"])
        self.centers = eval(config["centers"])
        self.clusters = eval(config["clusters"])
        self.k_clusters = len(self.clusters)

        lo = np.array([np.float64(-1.0)] * self.k_clusters)
        hi = np.array([np.float64(1.0)] * self.k_clusters)

        self.observation_space = spaces.Box(lo, hi, shape=(self.k_clusters,), dtype=np.float64)
        self.action_space = spaces.Discrete(self.k_clusters)

        # load the dataset
        self.dataset = self.load_data(config["dataset"])


    def _warm_start (self):
        """
        attempt a warm start for the rec sys, by sampling
        half of the dense submatrix of most-rated items
        """
        sample_size = round(len(self.dense) / 2.0)

        for action, items in self.clusters.items():
            for item in random.sample(self.dense, sample_size):
                if item in items:
                    state, reward, done, info = self.step(action)


    def _get_state (self):
        """
        calculate root-mean-square (i.e., normalized vector distance)
        for the agent's current "distance" measure from each cluster
        center as the observation
        """
        n = float(len(self.used))

        if n > 0.0:
            state = [ np.sqrt(x / n) for x in self.coords ]
        else:
            state = self.coords

        assert state in self.observation_space, (n, self.coords, state)
        return state


    def reset (self):
        """
        reset the item recommendation history, select a new user to
        simulate from among the dataset rows, then run through an
        initial 'warm-start' sequence of steps before handing step
        control back to the agent
        """
        self.count = 0
        self.used = []
        self.depleted = 0
        self.coords = [np.float64(0.0)] * self.k_clusters

        # select a random user to simulate
        self.data_row = random.choice(self.dataset)

        # attempt a warm start
        self._warm_start()

        return self._get_state()


    def step (self, action):
        """
        attempt to recommend one item; may result in a no-op --
        in other words, in production skip any repeated items
        """
        assert action in self.action_space, action
        assert_info = "c[item] {}, rating {}, scaled_diff {}"

        # enumerate items from the cluster selected by the action that
        # haven't been recommended previously to the simulated user
        items = set(self.clusters[action]).difference(set(self.used))

        if len(items) < 1:
            # oops! items from the selected cluster have been
            # depleted, i.e. all have been recommended previously to
            # the simulated user; hopefully the agent will learn to
            # switch to exploring among the other clusters
            self.depleted += 1
            item = None
            reward = self.REWARD_DEPLETED
        else:
            # chose an item from the selected cluster
            item = random.choice(list(items))
            rating = self.data_row[item]

            if not rating:
                # misfire! this action=>item resulted in an unrated
                # item
                reward = self.REWARD_UNRATED

            else:
                # success! this action=> resulted in an item rated by
                # the simulated user
                reward = rating
                self.used.append(item)

                # update the coords history: the agent observes the
                # evolving distance to each cluster
                for i in range(len(self.coords)):
                    c = self.centers[i]
                    scaled_diff = abs(c[item] - rating) / 2.0
                    assert scaled_diff <= 1.0, assert_info.format(c[item], rating, scaled_diff)
                    self.coords[i] += scaled_diff ** 2.0
                    assert self.coords[i] < len(self.used), (self.coords[i], scaled_diff ** 2.0)

        self.count += 1
        done = self.count >= self.MAX_STEPS
        info = { "item": item, "count": self.count, "depleted": self.depleted }

        return self._get_state(), reward, done, info


    def render (self, mode="human"):
        last_used = self.used[-10:]
        last_used.reverse()
            
        print(">> used:", last_used)
        print(">> dist:", [round(x, 2) for x in self._get_state()])

        print(">> depl:", self.depleted)
        #print(">> data:", self.data_row)


    def seed (self, seed=None):
        """Sets the seed for this env's random number generator(s).

        Note:
            Some environments use multiple pseudorandom number generators.
            We want to capture all such seeds used in order to ensure that
            there aren't accidental correlations between multiple generators.

        Returns:
            list<bigint>: Returns the list of seeds used in this env's random
              number generators. The first value in the list should be the
              "main" seed, or the value which a reproducer should pass to
              'seed'. Often, the main seed equals the provided 'seed', but
              this won't be true if seed=None, for example.
        """
        self.np_random, seed = seeding.np_random(seed)
        return [seed]


    def close (self):
        """Override close in your subclass to perform any necessary cleanup.
        Environments will automatically close() themselves when
        garbage collected or when the program exits.
        """
        pass


    ######################################################################
    ## load the dataset

    @classmethod
    def load_data (cls, data_path):
        """
        load the training data

        Jester collaborative filtering dataset (online joke recommender)
        https://goldberg.berkeley.edu/jester-data/

        This data file contains anonymous ratings from 24,983 users who 
        have rated 36 or more jokes.

        This is organized as a matrix with dimensions 24983 X 101

          * one row per user
          * first column gives the number of jokes rated by that user
          * the next 100 columns give the ratings for jokes 01 - 100
          * ratings are real values ranging from -10.00 to +10.00
          * the value "99" corresponds to "null" = "not rated"

        A dense sub-matrix, in which almost all users have rated the 
        jokes, includes these columns:

            {5, 7, 8, 13, 15, 16, 17, 18, 19, 20}

        See the discussion of "universal queries" in:

            Eigentaste: A Constant Time Collaborative Filtering Algorithm
            Ken Goldberg, Theresa Roeder, Dhruv Gupta, Chris Perkins
            Information Retrieval, 4(2), 133-151 (July 2001)
            https://goldberg.berkeley.edu/pubs/eigentaste.pdf
        """
        rows = []
        assert_info = "input data: i {} row {} rating {}"

        with open(data_path, newline="") as csvfile:
            csvreader = csv.reader(csvfile, delimiter=",")

            for row in csvreader:
                conv = [None] * (len(row) - 1)

                for i in range(1, len(row)):
                    if row[i] != cls.NO_RATING:
                        rating = float(row[i]) / cls.MAX_RATING
                        assert rating >= -1.0 and rating <= 1.0, assert_info.format(i, row, rating)
                        conv[i - 1] = rating

                rows.append(conv)

        return rows


    ######################################################################
    ## K-means clustering using scikit-learn

    @classmethod
    def cluster_sample (cls, k, sample):
        df = pd.DataFrame(sample)

        # impute missing values using the column means (i.e., the avg
        # rating per item)
        # https://scikit-learn.org/stable/modules/impute.html
        imp = SimpleImputer(missing_values=np.nan, strategy="mean")
        imp.fit(df.values)
        X = imp.transform(df.values).T

        # perform K-means clustering
        # https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html
        km = KMeans(n_clusters=k)
        km.fit(X)
        centers = km.cluster_centers_

        # segment the items by their respective cluster labels
        clusters = defaultdict(set)
        labels = km.labels_

        for i in range(len(labels)):
            clusters[labels[i]].add(i)

        return centers.tolist(), dict(clusters)


    @classmethod
    def prep_config (cls, dataset_path, k_clusters=3, debug=False, verbose=False):
        """we've previously used inertia to estimate the `k`
        hyperparameter to tune for the number of clusters (i.e.,
        user segmentation)

        https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_stability_low_dim_dense.html
        https://towardsdatascience.com/k-means-clustering-with-scikit-learn-6b47a369a83c
        """
        sample = cls.load_data(dataset_path)
        centers, clusters = cls.cluster_sample(k_clusters, sample)

        # use the results of the sample clustering to prepare a
        # configuration for our custom environment
        config = ppo.DEFAULT_CONFIG.copy()

        config["log_level"] = ("DEBUG" if verbose else "WARN")
        config["num_workers"] = (0 if debug else 3)

        config["env_config"] = {
            "dataset": dataset_path,
            "dense": str(cls.DENSE_SUBMATRIX),
            "clusters": repr(clusters),
            "centers": repr(centers),
            }

        return config


    ######################################################################
    ## managing rollouts

    @classmethod
    def run_one_episode (cls, config_env, naive=False, verbose=False):
        """
        step through one episode of the agent without learning, using
        either a naive strategy or random actions
        """
        env = cls(config_env)
        env.reset()
        sum_reward = 0

        action = None
        avoid_actions = set([])
        depleted = 0

        for i in range(env.MAX_STEPS):
            if not naive or not action:
                action = env.action_space.sample()

            state, reward, done, info = env.step(action)

            if verbose:
                print("action:", action)
                print("obs:", i, state, reward, done, info)
                #env.render()

            if naive:
                if info["depleted"] > depleted:
                    depleted = info["depleted"]
                    avoid_actions.add(action)

                # naive strategy: optimize for selecting items from
                # the nearest non-depleted cluster
                obs = []

                for a in range(len(state)):
                    if a not in avoid_actions:
                        dist = round(state[a], 2)
                        obs.append([dist, a])

                action = min(obs)[1]

            sum_reward += reward

            if done:
                if verbose:
                    print("DONE @ step {}".format(i))

                break

        if verbose:
            print("CUMULATIVE REWARD: ", round(sum_reward, 3))

        return sum_reward


    @classmethod
    def measure_baseline (cls, config_env, n_iter=1, naive=False, verbose=False):
        """
        measure the baseline performance without learning, using
        either a naive agent or random actions
        """
        history = []

        for episode in tqdm(range(n_iter), ascii=True, desc="measure baseline"):
            sum_reward = cls.run_one_episode(config_env, naive=naive, verbose=verbose)
            history.append(sum_reward)

        baseline = sum(history) / len(history)
        return baseline


    @classmethod
    def run_rollout (cls, agent, env, n_iter, verbose=False):
        """
        iterate through `n_iter` episodes in a rollout to emulate
        deployment in a production use case
        """
        for episode in range(n_iter):
            state = env.reset()
            sum_reward = 0

            for step in range(cls.MAX_STEPS):
                try:
                    action = agent.compute_action(state)
                    state, reward, done, info = env.step(action)

                    sum_reward += reward
                    print("reward {:6.3f}  sum {:6.3f}".format(reward, sum_reward))

                    if verbose:
                        env.render()
                except Exception:
                    traceback.print_exc()

                if done:
                    # report at the end of each episode
                    print("CUMULATIVE REWARD:", round(sum_reward, 3), "\n")
                    break


######################################################################
## command line interface and utilities

PARSER = ArgumentParser()

PARSER.add_argument("--full",
                    action="store_true",
                    dest="full_run",
                    default=False,
                    help="full optimization, not merely a minimal run"
                    )

PARSER.add_argument("--train",
                    default=None,
                    help="specify the number of training iterations"
                    )

PARSER.add_argument("--data",
                    default=None,
                    help="specify a dataset to use for rollouts"
                    )

PARSER.add_argument("-d", "--debug",
                    action="store_true",
                    dest="debug",
                    default=False,
                    help="debug mode, enables `pdb`"
                    )

PARSER.add_argument("-v", "--verbose",
                    action="store_true",
                    dest="verbose",
                    default=False,
                    help="verbose mode"
                    )


def parse_args ():
    """
    parse the CLI arguments to set parameters for running the app
    """
    args = PARSER.parse_args()

    if args.full_run:
        PARAM = {
            "baseline_iter": 10,
            "train_iter": 30,
            "rollout_iter": 5,
            }
    else:
        print("minimal run, to exercise the code")
        PARAM = {
            "baseline_iter": 3,
            "train_iter": 4,
            "rollout_iter": 1,
            }

    if args.train:
        PARAM["train_iter"] = int(args.train)

    PARAM["debug"] = args.debug
    PARAM["verbose"] = args.verbose
    PARAM["k_clusters"] = 12
    PARAM["dataset"] = "jester-data-1.csv"
    PARAM["checkpoint_root"] = "tmp/rec"
    PARAM["rollout_dataset"] = args.data

    return PARAM


def init_dir (checkpoint_root):
    """
    initialize the directory in which to save checkpoints, and the
    directory in which to log results
    """
    shutil.rmtree(checkpoint_root, ignore_errors=True, onerror=None)

    ray_results = "{}/ray_results/".format(os.getenv("HOME"))
    shutil.rmtree(ray_results, ignore_errors=True, onerror=None)


def get_best_checkpoint (df):
    """
    use a pareto archive to select the best checkpoint
    """
    df_front = df.drop(columns=["steps", "checkpoint"])
    mask = paretoset(df_front, sense=["max", "max", "max"])

    optimal = df_front[mask]
    max_val = optimal["avg_reward"].max()

    best_checkpoint = df.loc[df["avg_reward"] == max_val, "checkpoint"].values[0]
    return best_checkpoint


######################################################################
## main entry point

def main ():   
    warnings.filterwarnings("ignore", category=DeprecationWarning) 

    # initialize logs, dataset, configuration
    PARAM = parse_args()
    init_dir(PARAM["checkpoint_root"])
    dataset_path = Path.cwd() / Path(PARAM["dataset"])

    CONFIG = JokeRec.prep_config(
        dataset_path,
        k_clusters=PARAM["k_clusters"],
        debug=PARAM["debug"],
        verbose=PARAM["verbose"]
        )

    # measure the baseline performance of a naive agent
    if PARAM["debug"]:
        pdb.set_trace()

    baseline = JokeRec.measure_baseline(
        CONFIG["env_config"],
        n_iter=PARAM["baseline_iter"],
        naive=True,
        verbose=PARAM["verbose"],
        )

    print("BASELINE CUMULATIVE REWARD", round(baseline, 3), "\n")

    # restart Ray, register our environment, and create an agent
    ray.init(ignore_reinit_error=True)

    env_key = "JokeRec-v0"
    register_env(env_key, lambda config_env: JokeRec(config_env))
    AGENT = ppo.PPOTrainer(CONFIG, env=env_key)

    # use RLlib to train a policy using PPO
    df = pd.DataFrame(columns=[ "min_reward", "avg_reward", "max_reward", "steps", "checkpoint"])
    status = "reward {:6.2f} {:6.2f} {:6.2f}  len {:4.2f}  saved {}"

    for i in range(PARAM["train_iter"]):
        result = AGENT.train()

        checkpoint_file = AGENT.save(PARAM["checkpoint_root"])
        row = [
            result["episode_reward_min"],
            result["episode_reward_mean"],
            result["episode_reward_max"],
            result["episode_len_mean"],
            checkpoint_file,
            ]

        df.loc[len(df)] = row
        print(status.format(*row))

    best_checkpoint = get_best_checkpoint(df)
    print("\n", "BEST CHECKPOINT:", best_checkpoint, "\n")

    # apply the trained policy in a rollout
    AGENT.restore(best_checkpoint)

    if PARAM["rollout_dataset"]:
        config["env_config"]["dataset"] = Path.cwd() / Path(PARAM["rollout_dataset"])

    JokeRec.run_rollout(
        AGENT,
        JokeRec(CONFIG["env_config"]),
        PARAM["rollout_iter"],
        verbose=PARAM["verbose"]
        )

    # examine the trained policy
    policy = AGENT.get_policy()
    model = policy.model
    print("\n", model.base_model.summary())

    # shutdown gracefully, kthxbai
    ray.shutdown()


if __name__ == "__main__":
    main()
