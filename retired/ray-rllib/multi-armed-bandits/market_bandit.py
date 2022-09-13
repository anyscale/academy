import gym
from gym.spaces import Discrete, Box
from gym.utils import seeding
import numpy as np
import random

class MarketBandit (gym.Env):

    def __init__ (self, config={}):
        self.max_inflation = config.get('max-inflation', DEFAULT_MAX_INFLATION)
        self.tickers = config.get('tickers', DEFAULT_TICKERS)
        self.data_file = config.get('data-file', DEFAULT_DATA_FILE)
        print(f"MarketBandit: max_inflation: {self.max_inflation}, tickers: {self.tickers}, data file: {self.data_file} (config: {config})")

        self.action_space = Discrete(4)
        self.observation_space = Box(
            low  = -self.max_inflation,
            high =  self.max_inflation,
            shape=(1, )
        )
        self.df = load_market_data(self.data_file)
        self.cur_context = None


    def reset (self):
        self.year = self.df["year"].min()
        self.cur_context = self.df.loc[self.df["year"] == self.year]["inflation"][0]
        self.done = False
        self.info = {}

        return [self.cur_context]


    def step (self, action):
        if self.done:
            reward = 0.
            regret = 0.
        else:
            row = self.df.loc[self.df["year"] == self.year]

            # calculate reward
            ticker = self.tickers[action]
            reward = float(row[ticker])

            # calculate regret
            max_reward = max(map(lambda t: float(row[t]), self.tickers))
            regret = round(max_reward - reward)

            # update the context
            self.cur_context = float(row["inflation"])

            # increment the year
            self.year += 1

            if self.year >= self.df["year"].max():
                self.done = True

        context = [self.cur_context]
        #context = self.observation_space.sample()

        self.info = {
            "regret": regret,
            "year": self.year
        }

        return [context, reward, self.done, self.info]


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
