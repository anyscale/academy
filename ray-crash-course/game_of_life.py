#!/usr/bin/env python
import numpy as np
import time

# A Conway's Game of Life implementation. Used in
# ../ray-core/04-DistributedStateWithActors.ipynb.

class Game:
    # TODO: Game memory grows unbounded; trim older states?
    def __init__(self, initial_state, rules):
        self.states = [initial_state]
        self.rules = rules

    def step(self, num_steps = 1):
        """Take 1 or more steps, returning a list of new states."""
        new_states = [self.rules.step(self.states[-1]) for _ in range(num_steps)]
        self.states.extend(new_states)
        return new_states

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

class ConwaysRules:
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
        new_state = State(grid = new_grid)
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


def new_game(grid_size):
    initial_state = State(size = grid_size)
    rules = ConwaysRules()
    game  = Game(initial_state=initial_state, rules=rules)
    return game

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Conway's Game of Life")
    parser.add_argument('--size', metavar='N', type=int, default=100, nargs='?',
        help='The size of the square grid for the game')
    parser.add_argument('--steps', metavar='N', type=int, default=500, nargs='?',
        help='The number of steps to run')

    args = parser.parse_args()
    print(f"""
Conway's Game of Life:
  Grid size:           {args.size}
  Number steps:        {args.steps}
""")

    def print_state(n, state):
        print(f'\nstate #{n}:\n{state}')

    game  = new_game(size = args.size)
    for step in range(args.steps):
        new_states = game.step()
        print_state(step, new_states[0])

if __name__ == "__main__":
    main()
