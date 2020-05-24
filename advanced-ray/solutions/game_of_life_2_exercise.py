#!/usr/bin/env python

import ray
import numpy as np
import time, sys, os
from queue import Queue
sys.path.append("../..")
from util.printing import pd

# A variation of the game of life code used in the Ray Crash Course and
# the Ray Actors Revisited lesson.
# Changes:
# 1. RayGame now takes an argument to limit the growth of the sequence of states.
# 2. Better implementation of ``step`` for multiple steps at once.
# 3. Test implementations of ``live_neighbors`` and ``apply_rules`` with new
#    faster default implementations.
# 4. A new ``RayConwaysRulesBlocks`` that computes updates in parallel blocks.
# 5. Relaxed previous requirement for square grids.
@ray.remote
class RayGame:
    def __init__(self, grid_dimensions, rules_id, trim_states_after=0):
        """
        Initialize the game.

        Args:
            grid_dimensions: The (M,N) sizes of the game.
            rules_id: The ``Rules`` actor for rules processing.
            trim_after: A positive ``int`` for the ``State`` history queue
                size (default: unbounded, which could exhaust memory!).
        """
        self.states = Queue(trim_states_after)
        initial_state = RayGame.State(dimensions = grid_dimensions)
        self.states.put(initial_state)
        self.current_state = initial_state
        self.rules_id = rules_id

    def get_states(self):
        return self.states

    def step(self, num_steps = 1):
        """
        Take 1 or more steps, returning a list of new states.

        Args:
            num_steps: The number of steps to take. Defaults to 1
        Returns:
            A ``num_steps``-long list of new states.
        """
        # This is a situation where calling ray.get inside a loop is okay,
        # because we must have the result before the next loop iteration.
        states_for_these_steps = []   # Return only the new states!
        state = self.current_state
        for _ in range(num_steps):
            new_state_id = self.rules_id.step.remote(self.current_state)
            self.current_state = ray.get(new_state_id)
            self.states.put(self.current_state)
            states_for_these_steps.append(self.current_state)
        return states_for_these_steps

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
            for i in range(state.x_dim):
                for j in range(state.y_dim):
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

        rules = np.ubyte([
            [0,0,1,1,0,0,0,0,0],
            [0,0,0,1,0,0,0,0,0]])

        def apply_rules2(self, i, j, state):
            """
            Instead of conditionals, what about a lookup table? The game
            rules shown in ``apply_rules()`` translate nicely to a lookup table,
            ``RayConwaysRules.rules``. It appears this change makes no significant
            difference in performance, but table lookup is definitely an elegant
            approach and could be more performant if the conditionals in
            ``apply_rules()`` were more complex.
            """
            num_live_neighbors = self.live_neighbors(i, j, state)
            cell = state.grid[i][j]  # default value is no change in state
            return RayConwaysRules.rules[cell][num_live_neighbors]

        def live_neighbors(self, i, j, state):
            """
            This is the fastest implementation.
            Wrap at boundaries (i.e., treat the grid as a 2-dim "toroid")
            """
            x = state.x_dim
            y = state.y_dim
            g = state.grid
            im1 = i-1 if i > 0   else x-1
            ip1 = i+1 if i < x-1 else 0
            jm1 = j-1 if j > 0   else y-1
            jp1 = j+1 if j < y-1 else 0
            return (g[im1][jm1] + g[im1][j] + g[im1][jp1] + g[i][jm1]
                + g[i][jp1] + g[ip1][jm1] + g[ip1][j] + g[ip1][jp1])

        def live_neighbors2(self, i, j, state):
            """
            The original implementation updated for nonsquare grids.
            While more concise, one of several constructs here is a little
            slower than the implementation above:
            1. Calling ``sum()``
            2. Doing modulo arithmatic (but live_neighbors3 suggests this isn't
               an issue)
            3. The list comprehension

            Wrap at boundaries (i.e., treat the grid as a 2-dim "toroid")
            To wrap at boundaries, when k-1=-1, that wraps itself;
            for k+1=state.size, we mod it (which works for -1, too)
            For simplicity, we count the cell itself, then subtact it
            """
            x = state.x_dim
            y = state.y_dim
            g = state.grid
            return sum([g[i2%x][j2%y] for i2 in [i-1,i,i+1]
                for j2 in [j-1,j,j+1]]) - g[i][j]

        def live_neighbors3(self, i, j, state):
            """
            Is calculating moduli too expensive? What if we compute the correct
            indices instead? In fact, the moduli are about 10% faster than the
            following:
            """
            x = state.x_dim
            y = state.y_dim
            g = state.grid
            i2s = [i-1,i,i+1]
            j2s = [j-1,j,j+1]
            if i == 0:
                i2s[0] = x-1
            elif i == x-1:
                i2s[2] = 0
            if j == 0:
                j2s[0] = y-1
            elif j == y-1:
                j2s[2] = 0
            return sum([g[i2][j2] for i2 in i2s for j2 in j2s]) - g[i][j]

    @ray.remote
    class RayConwaysRulesBlocks():
        """
        Apply the rules to a state and return a new state.
        This version supports parallel computation of blocks of rows, rather
        than updating the cells serially.
        """
        def __init__(self, block_size = -1):
            """
            Process the grid updates in parallel "blocks" of size block_size.
            Args:
                block_size: The size of blocks. By default, it does the whole
                    thing as a single block.
            """
            self.block_size = block_size

        def step(self, state):
            """
            Determine the next values for all the cells, based on the current
            state. Creates a new State with the changes.
            A new implementation that parallizes execution of blocks of rows.
            """
            xsize = state.x_dim
            bsize = self.block_size if self.block_size > 0 else xsize
            def delta(i):
                d = i+bsize
                return d if d <= xsize else xsize
            indices = [(i,delta(i)) for i in range(0, xsize, bsize)]

            block_ids = [apply_rules_block.remote(i, j, state) for i,j in indices]
            blocks = ray.get(block_ids)
            new_grid = np.zeros((xsize, state.y_dim), dtype=int)
            for block_index in range(len(blocks)):
                i,j = indices[block_index]
                new_grid[i:j] = blocks[block_index]
            new_state = RayGame.State(grid = new_grid)
            return new_state


    class State:
        """
        Represents a grid of game cells.
        Each instance is considered immutable.
        """
        def __init__(self, grid = None, dimensions = (100, 100)):
            """
            Create a State. Specify either a grid of cells or a tuple
            for the x and y sizes.

            Args:
                grid: The grid of cells. Specify this or the sizes.
                dimensions: Tuple (or two-element list) with the x and y
                    grid sizes, for which a grid of x * y sizes will be
                    initialized with random values.
            """
            if type(grid) != type(None): # Avoid annoying AttributeError
                self.x_dim = grid.shape[0]
                self.y_dim = grid.shape[1]
                self.grid = grid  # No need to copy as this is not modified!
            else:
                self.x_dim, self.y_dim = dimensions
                self.grid = np.random.randint(2,
                    size = self.x_dim * self.y_dim).reshape(
                    (self.x_dim, self.y_dim))

        def living_cells(self):
            """
            Returns ([x1, x2, ...], [y1, y2, ...]) for all living cells.
            Simplifies graphing.
            """
            cells = [(i,j) for i in range(self.x_dim)
                for j in range(self.y_dim) if self.grid[i][j] == 1]
            return zip(*cells)

        def json(self, indent=2):
            list = self.grid.tolist()
            return json.dumps(list, indent=indent)

        def __str__(self):
            s = ' |\n| '.join([' '.join(map(lambda x: '*'
                    if x else ' ', self.grid[i])) for i in range(self.x_dim)])
            return '| ' + s + ' |'


@ray.remote
def apply_rules_block(start, end, state):
    """
    Use a separate Ray task for computing a block update, rather than a
    method that can only run in the ``RayConwaysRulesBlocks`` actor's worker.
    Otherwise, this implementation follows ``RayConwaysRules.apply_rules``.
    Args:
        start: Starting row index in ``State.grid`` for this block, inclusive.
        end: Ending row index in ``State.grid`` for this block, exclusive.
        state: The current ``State`` object.
    """
    x = state.x_dim
    y = state.y_dim
    g = state.grid
    block = g[start:end].copy()
    for n in range(end-start):
        i = n+start
        for j in range(y):
            im1 = i-1 if i > 0   else x-1
            ip1 = i+1 if i < x-1 else 0
            jm1 = j-1 if j > 0   else y-1
            jp1 = j+1 if j < y-1 else 0
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

def time_ray_games(num_games = 1, max_steps = 100, batch_size = 1, grid_dimensions = (100,100), use_block_updates=True, block_size=100):
    rules_ids = []
    game_ids = []
    for i in range(num_games):
        if use_block_updates:
            rules_id = RayGame.RayConwaysRulesBlocks.remote(block_size)
        else:
            rules_id = RayGame.RayConwaysRules.remote()
        game_id  = RayGame.remote(grid_dimensions, rules_id)
        game_ids.append(game_id)
        rules_ids.append(rules_id)
    print(f'rules_ids:\n{rules_ids}')  # these will produce more interesting flame graphs!
    print(f'game_ids:\n{game_ids}')
    start = time.time()
    state_ids = []
    for game_id in game_ids:
        for i in range(int(max_steps/batch_size)):  # Do a total of max_steps game steps, which is max_steps/delta_steps
            state_ids.append(game_id.step.remote(batch_size))
    ray.get(state_ids)  # wait for everything to finish! We are ignoring what ray.get() returns, but what will it be??
    pd(time.time() - start, prefix = f'Total time for {num_games} games (max_steps = {max_steps}, batch_size = {batch_size})')


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Conway's Game of Life v2")
    parser.add_argument('-d', '--dimensions', metavar='X*Y', type=str, default='100*100', nargs='?',
        help='The 2D grid dimensions. Use "X,Y" or "X*Y". Only one pair can be specified, because the other arguments really need to be "sensible" for this value.')
    parser.add_argument('-s', '--steps', metavar='N', type=int, default=500, nargs='?',
        help='The number of steps to run')
    parser.add_argument('-b', '--blocks', help="Use block updates rather than synchronous",
        action='store_true')
    parser.add_argument('--block-size', metavar='N', type=int, default=-1, nargs='?',
        help='If --blocks specified, then the size of the blocks')
    parser.add_argument('-l', '--local', help="Run Ray locally. Default is to join a cluster",
        action='store_true')

    args = parser.parse_args()
    print(f"""
Conway's Game of Life v2:
  Grid dimentions:     {args.dimensions}
  Number steps:        {args.steps}
  Use block updates?   {args.blocks}
  Block size:          {args.block_size}
  Run Ray locally?     {args.local}
""")

    delim = ',' if args.dimensions.find(',') > 0 else '*'
    x_dim, y_dim = list(map(lambda s: int(s), args.dimensions.split(delim)))

    if args.local:
        ray.init()
    else:
        ray.init(address='auto')

    time_ray_games(num_games = 1, max_steps = args.steps, batch_size = 1, grid_dimensions = (x_dim,y_dim), use_block_updates=args.blocks, block_size=args.block_size)

if __name__ == "__main__":
    main()
