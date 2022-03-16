#!/usr/bin/env python

import ray
import numpy as np
import time, sys, os
sys.path.append("..")
from util.printing import pd

# A variation of the game of life code used in the Ray Crash Course.
@ray.remote
class RayGame:
    # TODO: Game memory grows unbounded; trim older states?
    def __init__(self, grid_size, rules_ref):
        self.states = [RayGame.State(size = grid_size)]
        self.rules_ref = rules_ref

    def get_states(self):
        return self.states

    def step(self, num_steps = 1):
        """Take 1 or more steps, returning a list of new states."""
        start_index = len(self.states)
        for _ in range(num_steps):
            new_state_ref = self.rules_ref.step.remote(self.states[-1])
            self.states.append(ray.get(new_state_ref))
        return self.states[start_index:-1]  # return the new states only!

    @ray.remote
    class RayConwaysRules:
        """
        Apply the rules to a state and return a new state.
        """
        def step(self, state):
            """
            Determine the next values for all the cells, based on the current
            state. Creates a new State with the changes.
            """
            new_grid = state.grid.copy()
            for i in range(state.size):
                for j in range(state.size):
                    lns = self.live_neighbors(i, j, state)
                    new_grid[i][j] = self.apply_rules(i, j, lns, state)
            new_state = RayGame.State(grid = new_grid)
            return new_state

        def apply_rules(self, i, j, live_neighbors, state):
            """
            Determine next value for a cell, which could be the same.
            The rules for Conway's Game of Life:
                Any live cell with fewer than two live neighbours dies, as if by underpopulation.
                Any live cell with two or three live neighbours lives on to the next generation.
                Any live cell with more than three live neighbours dies, as if by overpopulation.
                Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
            """
            cell = state.grid[i][j]  # default value is no change in state
            if cell == 1:
                if live_neighbors < 2 or live_neighbors > 3:
                    cell = 0
            elif live_neighbors == 3:
                cell = 1
            return cell

        def live_neighbors(self, i, j, state):
            """
            Wrap at boundaries (i.e., treat the grid as a 2-dim "toroid")
            To wrap at boundaries, when k-1=-1, that wraps itself;
            for k+1=state.size, we mod it (which works for -1, too)
            For simplicity, we count the cell itself, then subtact it
            """
            s = state.size
            g = state.grid
            return sum([g[i2%s][j2%s] for i2 in [i-1,i,i+1] for j2 in [j-1,j,j+1]]) - g[i][j]

    class State:
        """
        Represents a grid of game cells.
        For simplicity, require square grids.
        Each instance is considered immutable.
        """
        def __init__(self, grid = None, size = 10):
            """
            Create a State. Specify either a grid of cells or a size, for
            which an size x size grid will be computed with random values.
            (For simplicity, only use square grids.)
            """
            if type(grid) != type(None): # avoid annoying AttributeError
                assert grid.shape[0] == grid.shape[1]
                self.size = grid.shape[0]
                self.grid = grid.copy()
            else:
                self.size = size
                # Seed: random initialization
                self.grid = np.random.randint(2, size = size*size).reshape((size, size))


        def living_cells(self):
            """
            Returns ([x1, x2, ...], [y1, y2, ...]) for all living cells.
            Simplifies graphing.
            """
            cells = [(i,j) for i in range(self.size) for j in range(self.size) if self.grid[i][j] == 1]
            return zip(*cells)

        def __str__(self):
            s = ' |\n| '.join([' '.join(map(lambda x: '*' if x else ' ', self.grid[i])) for i in range(self.size)])
            return '| ' + s + ' |'

def time_ray_games(num_games = 1, max_steps = 100, batch_size = 1, grid_size = 100):
    rules_refs = []
    game_refs = []
    for i in range(num_games):
        rules_ref = RayGame.RayConwaysRules.remote()
        game_ref  = RayGame.remote(grid_size, rules_ref)
        game_refs.append(game_ref)
        rules_refs.append(rules_ref)
    print(f'rules_refs:\n{rules_refs}')  # these will produce more interesting flame graphs!
    print(f'game_refs:\n{game_refs}')
    start = time.time()
    state_refs = []
    for game_ref in game_refs:
        for i in range(int(max_steps/batch_size)):  # Do a total of max_steps game steps, which is max_steps/delta_steps
            state_refs.append(game_ref.step.remote(batch_size))
    ray.get(state_refs)  # wait for everything to finish! We are ignoring what ray.get() returns, but what will it be??
    pd(time.time() - start, prefix = f'Total time for {num_games} games (max_steps = {max_steps}, batch_size = {batch_size})')


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Conway's Game of Life v2")
    parser.add_argument('--size', metavar='N', type=int, default=100, nargs='?',
        help='The size of the square grid for the game')
    parser.add_argument('--steps', metavar='N', type=int, default=500, nargs='?',
        help='The number of steps to run')
    parser.add_argument('-l', '--local', help="Run Ray locally. Default is to join a cluster",
        action='store_true')

    args = parser.parse_args()
    print(f"""
Conway's Game of Life v2:
  Grid size:           {args.size}
  Number steps:        {args.steps}
  Run Ray locally?     {args.local}
""")

    if args.local:
        ray.init()
    else:
        ray.init(address='auto')

    time_ray_games(num_games = 1, max_steps = args.steps, batch_size = 1, grid_size = args.size)

if __name__ == "__main__":
    main()
