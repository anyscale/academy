#!/usr/bin/env python
import numpy as np
import time
import ray

# One solution for Exercise 4. This one finds that a better implementation of
# live_neighbors can improve performance about 40%. The alternative
# implementations are also here. See also micro-perf-tests.py, which was used
# to more easily test the different implementations.
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

@ray.remote
class RayConwaysRules():
    """
    Apply the rules to a state and return a new state.
    """

    def step(self, state):
        """
        Determine the next values for all the cells, based on the current
        state. Creates a new State with the changes.
        The original implementation.
        """
        new_grid = state.grid.copy()
        for i in range(state.size):
            for j in range(state.size):
                new_grid[i][j] = self.apply_rules(i, j, state)
        new_state = State(grid = new_grid)
        return new_state

    def apply_rules(self, i, j, state):
        """
        Determine next value for a cell, which could be the same.
        The rules for Conway's Game of Life:
            Any live cell with fewer than two live neighbours dies, as if by underpopulation.
            Any live cell with two or three live neighbours lives on to the next generation.
            Any live cell with more than three live neighbours dies, as if by overpopulation.
            Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
        """
        num_live_neighbors = self.live_neighbors(i, j, state)
        cell = state.grid[i][j]  # default value is no change in state
        if cell == 1:
            if num_live_neighbors < 2 or num_live_neighbors > 3:
                cell = 0
        elif num_live_neighbors == 3:
            cell = 1
        return cell

    rules = np.ubyte([
        [0,0,1,1,0,0,0,0,0],
        [0,0,0,1,0,0,0,0,0]])

    def apply_rules2(self, i, j, state):
        """
        Instead of conditionals, what about a lookup table? The game
        rules translate nicely to a lookup table, RayConwaysRules.rules.
        It appears this change makes no difference in performance, but
        table lookup is definitely an elegant approach and could be more
        performant if the conditionals in "apply_rules" were more complex.
        """
        num_live_neighbors = self.live_neighbors(i, j, state)
        cell = state.grid[i][j]  # default value is no change in state
        return RayConwaysRules.rules[cell][num_live_neighbors]

    def live_neighbors(self, i, j, state):
        """
        This is the fastest implementation.
        Wrap at boundaries (i.e., treat the grid as a 2-dim "toroid")
        """
        s = state.size
        g = state.grid
        im1 = i-1 if i > 0   else s-1
        ip1 = i+1 if i < s-1 else 0
        jm1 = j-1 if j > 0   else s-1
        jp1 = j+1 if j < s-1 else 0
        return g[im1][jm1] + g[im1][j] + g[im1][jp1] + g[i][jm1] + g[i][jp1] + g[ip1][jm1] + g[ip1][j] + g[ip1][jp1]

    def live_neighbors2(self, i, j, state):
        """
        The original implementation. While more concise, one of several
        constructs here is a little slower than the implementation above:
        1. Calling sum
        2. Doing modulo arithmatic (but live_neighbors3 suggests this isn't an issue)
        3. The list comprehension
        To wrap at boundaries, when k-1=-1, that wraps itself;
        for k+1=state.size, we mod it (which works for -1, too)
        For simplicity, we count the cell itself, then subtact it
        """
        s = state.size
        g = state.grid
        return sum([g[i2%s][j2%s] for i2 in [i-1,i,i+1] for j2 in [j-1,j,j+1]]) - g[i][j]

    def live_neighbors3(self, i, j, state):
        """
        Is calculating moduli too expensive? What if we compute the correct indices
        instead? In fact, the moduli are about 10% faster than the following:
        """
        s = state.size
        g = state.grid
        i2s = [i-1,i,i+1]
        j2s = [j-1,j,j+1]
        if i == 0:
            i2s[0] = s-1
        elif i == s-1:
            i2s[2] = 0
        if j == 0:
            j2s[0] = s-1
        elif j == s-1:
            j2s[2] = 0
        return sum([g[i2][j2] for i2 in i2s for j2 in j2s]) - g[i][j]

@ray.remote
class RayGame2:
    # TODO: Game memory grows unbounded; trim older states?
    def __init__(self, initial_state, rules_id):
        self.states = [initial_state]
        self.rules_id = rules_id

    def step(self, num_steps = 1):
        """Take 1 or more steps, returning a list of new states."""
        start_index = len(self.states)
        for _ in range(num_steps):
            new_state_id = self.rules_id.step.remote(self.states[-1])
            self.states.append(ray.get(new_state_id))
        return self.states[start_index:-1]  # return the new states only!

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Conway's Game of Life")
    parser.add_argument('--size', metavar='N', type=int, default=100, nargs='?',
        help='The size of the square grid for the game')
    parser.add_argument('--steps', metavar='N', type=int, default=500, nargs='?',
        help='The number of steps to run')
    parser.add_argument('--batch_size', metavar='N', type=int, default=1, nargs='?',
        help='Process grid updates in batches of batch_size steps')
    parser.add_argument('--verbose', help="Print invocation parameters",
        action='store_true')
    parser.add_argument('--pause', help="Don't exit immediately, wait for user acknowledgement",
        action='store_true')

    args = parser.parse_args()

    if args.verbose:
        print(f"""
Conway's Game of Life:
  Grid size:             {args.size}
  Number steps:          {args.steps}
  Batch size:            {args.batch_size}
  Pause before existing? {args.pause}
""")

    ray.init()
    print(f'Ray Dashboard: http://{ray.get_webui_url()}')

    def print_state(n, state):
        print(f'\nstate #{n}:\n{state}')

    def pd(d, prefix=''):
        print('{:s} duration = {:6.3f}'.format(prefix, d))

    def time_ray_games4(num_games = 1, max_steps = args.steps, batch_size = args.batch_size, grid_size = args.size):
        game_ids = [RayGame2.remote(State(size = grid_size), RayConwaysRules.remote()) for i in range(num_games)]
        start = time.time()
        state_ids = []
        for game_id in game_ids:
            for i in range(int(max_steps/batch_size)):  # Do a total of max_steps game steps, which is max_steps/delta_steps
                state_ids.append(game_id.step.remote(batch_size))
        ray.get(state_ids)  # wait for everything to finish! We are ignoring what ray.get() returns, but what will it be??
        pd(time.time() - start, prefix = f'Total time for {num_games} games (grid size = {grid_size}, max steps = {max_steps}, batch size = {batch_size})')
        return game_ids  # for cleanup afterwards


    for _ in range(4):
        time_ray_games4(num_games = 1, max_steps = args.steps, batch_size=args.batch_size, grid_size=args.size)

    if args.pause:
        input("Hit return when finished: ")

if __name__ == "__main__":
    main()
