#!/usr/bin/env python
import numpy as np
import time, os, sys, json
from datetime import datetime
from queue import Queue
import ray

# Last solution for Exercise 4. This implementation processes
# grid updates in parallel "blocks". That is, instead of processing
# a new grid sequentially, blocks of rows are processed in parallel.
class State:
    """
    Represents a grid of game cells.
    Each instance is considered immutable.
    """
    def __init__(self, grid = None, dimensions = (10, 10)):
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
        for i in range(state.x_dim):
            for j in range(state.y_dim):
                new_grid[i][j] = self.apply_rules(i, j, state)
        new_state = State(grid = new_grid)
        return new_state

    def apply_rules(self, i, j, state):
        """
        Determine next value for a cell, which could be the same.
        The rules for Conway's Game of Life:
            Any live cell with fewer than two live neighbours dies,
                as if by underpopulation.
            Any live cell with two or three live neighbours lives on
                to the next generation.
            Any live cell with more than three live neighbours dies,
                as if by overpopulation.
            Any dead cell with exactly three live neighbours becomes
                a live cell, as if by reproduction.
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
        The original implementation. While more concise, one of several
        constructs here is a little slower than the implementation above:
        1. Calling ``sum()``
        2. Doing modulo arithmatic (but live_neighbors3 suggests this isn't
           an issue)
        3. The list comprehension
        To wrap at boundaries, when ``k-1=-1``, that wraps itself;
        for ``k+1=state.?_dim``, we take the modulus of it (which also works
        for -1, too) For simplicity, we count the cell, then subtract it.
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
        new_state = State(grid = new_grid)
        return new_state

@ray.remote
class RayGame:
    """
    The only reason to make ``RayGame`` an actor is to support multiple
    concurrent games.
    """

    def __init__(self, initial_state, rules_id, trim_states_after=0):
        """
        Initialize the game.

        Args:
            initial_state: The initial game ``State``.
            rules_id: The ``Rules`` actor for rules processing.
            trim_after: A positive ``int`` for the ``State`` history queue
                size (default: unbounded, which could exhaust memory!).
        """
        self.states = Queue(trim_states_after)
        self.states.put(initial_state)
        self.current_state = initial_state
        self.rules_id = rules_id

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

    def get_states(self):
        """
        A getter method for the history of ``States``; required for actors.
        """
        return self.states

    def get_current_state(self):
        """
        A getter method for the current ``State``; required for actors.
        """
        return self.current_state

@ray.remote
def run_game(game_number, runs, old_rules_impl,
    x_dim, y_dim, step_sizes, batch_sizes, block_sizes,
    verbose, write_states):

    def now():
        now = datetime.now()
        return now.strftime("%Y_%m_%d-%H_%M_%S.%f")

    old_rules_str = 'old-rules' if old_rules_impl else 'new-rules'
    test_dir = os.path.abspath(os.path.dirname(__file__)) + "/test-runs"
    base_name = os.path.splitext(os.path.basename(__file__))[0] # remove .py too!
    os.makedirs(test_dir, exist_ok=True)
    csv_file  = '{:s}-game{:02d}-{:s}-{:s}.csv'.format(base_name, game_number, old_rules_str, now())

    def write_states_to_json(states, steps, batch, block, run):
        json_file = '{:s}-states-{:03d}-{:03d}-{:03d}-{:03d}-game{:02d}-{:s}-{:s}.json'.format(
            base_name, steps, batch, block, run, game_number, old_rules_str, now())
        if verbose:
            print(f'Writing JSON data to {test_dir}/{json_file}')
        with open(f'{test_dir}/{json_file}', 'a') as jfile:
            metadata = {
                'steps':      steps,
                'batch':      batch,
                'block':      block,
                'run':        run,
                'game':       game_number,
                'old_or_new': 'old_rules_str'
            }
            content = {
                'metadata': metadata,
                'states': [state.grid.tolist() for state_list in states for state in state_list]
            }
            js = json.dumps(content, indent=2)
            print(js)
            jfile.write(js+'\n')


    if verbose:
        print(f'Writing CSV data to {test_dir}/{csv_file}')
    game_ids = []
    with open(f'{test_dir}/{csv_file}', 'a') as csv:
        csv.write('x_dim,y_dim,steps,batch_size,row_block_size,time_mean,time_stddev\n')
        for steps in step_sizes:
            for batch in batch_sizes:
                if batch > steps:
                    print(f'ERROR: batch size {batch} > number of steps {steps}. Skipping...')
                    continue
                for block in block_sizes:
                    durations = np.zeros(runs)
                    for run in range(runs):
                        rules_id = None
                        if old_rules_impl:
                            rules_id = RayConwaysRules.remote()
                        else:
                            rules_id = RayConwaysRulesBlocks.remote(block)
                        game_id = RayGame.remote(State(dimensions = (x_dim, y_dim)), rules_id)
                        game_ids.append(game_id)
                        start = time.time()
                        state_ids = []
                        for i in range(int(steps/batch)):  # Do a total of steps game steps, which is steps/batch
                            state_ids.append(game_id.step.remote(batch))
                        states = ray.get(state_ids)  # wait for everything to finish! We are ignoring what ray.get() returns, but what will it be??
                        if write_states:
                            write_states_to_json(states, steps, batch, block, run)
                        durations[run] = time.time() - start
                    mean = np.mean(durations)
                    stddev = np.std(durations)
                    print('Grid size: {:d}*{:d}, max steps: {:d}, batch size: {:d}, # rows in block = {:d}, duration: mean = {:7.4} stddev = {:7.4}'.format(
                            x_dim, y_dim, steps, batch, block, mean, stddev))
                    csv.write('{:d},{:d},{:d},{:d},{:d},{:7.4},{:7.4}\n'.format(
                            x_dim, y_dim, steps, batch, block, mean, stddev))
        return game_ids

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Conway's Game of Life. The number of games is len(games)*len(steps)*len(batch_sizes)*len(num_blocks)*")
    parser.add_argument('--games', metavar='N', type=int, default=1, nargs='?',
        help='The number of concurrent games to run. Defaults to 1.')
    parser.add_argument('--runs', metavar='N', type=int,
        help="How many runs for each parameter set")
    parser.add_argument('--dimensions', metavar='X*Y', type=str, default='100*100', nargs='?',
        help='The 2D grid dimensions. Use "X,Y" or "X*Y". Only one pair can be specified, because the other arguments really need to be "sensible" for this value.')
    parser.add_argument('--steps', metavar='n1,n2,...', type=str, default='500', nargs='?',
        help='Comma-separated list of the numbers of steps to take per game.')
    parser.add_argument('--batches', metavar='n1,n2,...', type=str, default='1', nargs='?',
        help='Comma-separated list of batch sizes for processing steps in batches per game (filtered for values <= # steps)')
    parser.add_argument('--blocks', metavar='n1,n2,...', type=str, default='1', nargs='?',
        help='Do runs where grid updates are performed in row blocks. (filtered for <= # rows)')
    parser.add_argument('--verbose', help="Print invocation parameters",
        action='store_true')
    parser.add_argument('--write_states', help="Print the states to a JSON file (for graphing)",
        action='store_true')
    parser.add_argument('--pause', help="Don't exit immediately, wait for user acknowledgement",
        action='store_true')
    parser.add_argument('--old_rules_implementation', help='Use the "pre-blockified" version of RaysConwaysRules (for comparison)',
        action='store_true')

    args = parser.parse_args()
    delim = ',' if args.dimensions.find(',') > 0 else '*'
    x_dim, y_dim = list(map(lambda s: int(s), args.dimensions.split(delim)))
    step_sizes   = list(map(lambda s: int(s), args.steps.split(',')))
    batch_sizes  = list(map(lambda s: int(s), args.batches.split(',')))
    block_sizes  = list(map(lambda s: int(s), args.blocks.split(',')))
    step_sizes.sort()
    batch_sizes.sort()
    block_sizes.sort()

    ignore_blocks = ''
    old_new = 'New'
    if args.old_rules_implementation:
        ignore_blocks = '(ignored; using the original Rules implementation.)'
        old_new = 'Old'
    if args.verbose:
        print(f"""
Conway's Game of Life:
  Number of concurrent games:          {args.games}
  Use old or new rules implementation? {old_new}
  Grid dimensions:                     {x_dim} * {y_dim}
  Number of runs per param set:        {args.runs}
  Number steps:                        {step_sizes}
  Batch sizes:                         {batch_sizes}
  Block sizes:                         {block_sizes} {ignore_blocks}
  Write states to JSON file?           {args.write_states}
  Pause before existing?               {args.pause}
""")
    if args.old_rules_implementation:
        block_sizes = [1]  # reset in this case

    ray.init()
    if args.verbose:
        print(f'Ray Dashboard: http://{ray.get_webui_url()}')

    game_ids = [run_game.remote(n, args.runs, args.old_rules_implementation,
        x_dim, y_dim, step_sizes, batch_sizes, block_sizes,
        args.verbose, args.write_states)
        for n in range(args.games)]
    ray.get(game_ids)  # Force program to not exit before they are done!

    if args.pause:
        input("Hit return when finished: ")

if __name__ == "__main__":
    main()
