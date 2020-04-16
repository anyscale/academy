#!/usr/bin/env python
import numpy as np
import time
import ray

# Last solution for Exercise 4. This implementation processes
# grid updates in parallel "blocks". That is, instead of processing
# a new grid sequentially, blocks of rows are processed in parallel.
# On a late 2019 13" MacBook Pro, using the default command line
# arguments, the performance improvement is noticable:
#
#  Ex-GameOfLife.py  (synchronous grid processing):
# Total time for 1 games (max_steps = 500, batch_size = 50) duration = 18.617
# Total time for 1 games (max_steps = 500, batch_size = 50) duration = 17.780
# Total time for 1 games (max_steps = 500, batch_size = 50) duration = 18.458
# Total time for 1 games (max_steps = 500, batch_size = 50) duration = 18.593
# avg = 18.362, std dev = 0.341
#
#  Ex-GameOfLife-blocks.py  (asynchronous blocks for grid processing):
# Total time for 1 games (max_steps = 500, batch_size = 50) duration = 17.840
# Total time for 1 games (max_steps = 500, batch_size = 50) duration = 17.601
# Total time for 1 games (max_steps = 500, batch_size = 50) duration = 18.063
# Total time for 1 games (max_steps = 500, batch_size = 50) duration = 17.423
# avg = 17.732, std dev = 0.242
#
# What's the improvement? 17.732/18.362 = 0.966 = ~97%
# So the improvement is only about 3%.
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
def apply_rules_block(start, end, state):
    """
    Args:
        start (int) starting row for this block, inclusive
        end   (int) ending row for this block, exclusive
        state (State) object
    """
    s = state.size
    g = state.grid
    block = g[start:end].copy()
    for n in range(end-start):
        i = n+start
        for j in range(s):
            im1 = i-1 if i > 0   else s-1
            ip1 = i+1 if i < s-1 else 0
            jm1 = j-1 if j > 0   else s-1
            jp1 = j+1 if j < s-1 else 0
            num_live_neighbors = (
                g[im1][jm1] + g[im1][j] + g[im1][jp1] +
                g[i][jm1] + g[i][jp1] +
                g[ip1][jm1] + g[ip1][j] + g[ip1][jp1])
            cell = block[n][j]  # default value is no change in state
            if cell == 1:
                if num_live_neighbors < 2 or num_live_neighbors > 3:
                    block[n][j] = 0
            elif num_live_neighbors == 3:
                block[n][j] = 1
    return block

@ray.remote
class RayConwaysRules():
    """
    Apply the rules to a state and return a new state.
    """
    def __init__(self, num_blocks = 1):
        """
        If num_blocks > 1, will process the grid updates in parallel "blocks".
        """
        self.num_blocks = num_blocks

    def step(self, state):
        """
        Determine the next values for all the cells, based on the current
        state. Creates a new State with the changes.
        New implementation that parallizes execution of blocks of rows.
        """
        block_size = int(state.size / self.num_blocks)
        def delta(i):
            d = i+block_size
            return d if d <= state.size else state.size
        indices = [(i,delta(i)) for i in range(0, state.size, self.num_blocks)]

        block_ids = [apply_rules_block.remote(i, j, state) for i, j in indices]
        blocks = ray.get(block_ids)
        new_grid = np.zeros((state.size, state.size), dtype=int)
        for block_index in range(len(blocks)):
            i,j = indices[block_index]
            new_grid[i:j] = blocks[block_index]
        new_state = State(grid = new_grid)
        return new_state

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
    parser.add_argument('--num_blocks', metavar='N', type=int, default=1, nargs='?',
        help='Process grid updates in num_blocks parallel groups')
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
  Number of row blocks:  {args.num_blocks}
  Pause before existing? {args.pause}
""")

    ray.init()
    print(f'Ray Dashboard: http://{ray.get_webui_url()}')

    def print_state(n, state):
        print(f'\nstate #{n}:\n{state}')

    def pd(d, prefix=''):
        print('{:s} duration = {:6.3f}'.format(prefix, d))

    def time_ray_games4(num_games = 1, max_steps = args.steps, batch_size = args.batch_size, grid_size = args.size, num_blocks = args.num_blocks):
        game_ids = [RayGame2.remote(State(size = grid_size), RayConwaysRules.remote(num_blocks)) for i in range(num_games)]
        start = time.time()
        state_ids = []
        for game_id in game_ids:
            for i in range(int(max_steps/batch_size)):  # Do a total of max_steps game steps, which is max_steps/delta_steps
                state_ids.append(game_id.step.remote(batch_size))
        ray.get(state_ids)  # wait for everything to finish! We are ignoring what ray.get() returns, but what will it be??
        pd(time.time() - start, prefix = f'Total time for {num_games} games (grid size = {grid_size}, max steps = {max_steps}, batch size = {batch_size}), num row blocks = {num_blocks}')
        return game_ids  # for cleanup afterwards


    for _ in range(4):
        time_ray_games4(num_games = 1, max_steps = args.steps, batch_size=args.batch_size, grid_size=args.size, num_blocks = args.num_blocks)

    if args.pause:
        input("Hit return when finished: ")

if __name__ == "__main__":
    main()
