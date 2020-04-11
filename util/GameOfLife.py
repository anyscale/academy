#!/usr/bin/env python
import numpy as np
import time

class Game:
	"""
	Conway's Game of Life.

	Args:
		state (State) encapsulates the game state
		rules (Rules) the rules for this game

	"""
	def __init__(self, state, rules):
		self.state = state
		self.rules = rules

	def step(self):
		self.state = self.rules.step(self.state)
		return self.state

	def run(self, max_steps = 1000, pause=0.0, foreach_state = None):
		"""
		Run the game for max_steps iterations, pausing pause seconds.

		Args:
			max_steps (int) the number of iterations
			pause (float) the number of seconds between iterations (default: 0)
			foreach_state (function) a function(n,state) to which each new state is passed.
		Returns:
			A list of all the grids computed during the game. The length is the number of steps.
		"""
		grids = [self.state.grid] # The grids at each iteration
		i = 0
		for i in range(max_steps):
			if pause > 0.0:
				time.sleep(pause)
			i += 1
			last_grid = self.state.grid.copy()
			self.step()
			if foreach_state:
				foreach_state(i, self.state)
			grids.append(self.state.grid)
			if (self.state.grid == last_grid).all():
				break
		return grids

class State:
	def __init__(self, grid = None, live_cells = None, size = -1):
		"""
		Construct a Game of Life state object that tracks the grid changes.
		Specify ONE of the following:
		1. a square grid,
		2. an array of live_cells with an optional size,
		3. or just a size.
		If the size is specified, a size x size grid is created with random live cells.
		Otherwise, the size is determined from the provided grid or cells.

		Args:
			grid (Numpy matrix): The full square grid for the current state
			live_cells (list of (x,y) tuples): Just the live grid
			size (int): Create an square grid of this size.
		"""
		self.size = size
		if grid != None:
			assert live_cells == None, "Can't specify both grid and live_cells"
			assert grid.shape(0) == grid.shape(1), "Only square grids are allowed"
			assert grid.shape(0) > 0, "Grids can't be zero sized"
			if size > 0:
				print(f'WARNING: since the grid was specified, ignoring the size argument ({size})')
			self.size = grid.shape(0)
			self.grid = grid.copy()
		elif live_cells != None:
			assert grid == None, "Can't specify both grid and live_cells"
			size1 = find_size(live_cells)
			assert size1 > 0, "The live_cells list is empty"
			if self.size > 0 and self.size < size1:
				print(f'WARNING: the specified size is to small is too small for the live_cells. Using the larger value ({size} vs. {size1})')
				self.size = size1
			self.grid = np.zeros((self.size, self.size))
			for x,y in live_cells:
				self.grid[x][y] = 1
		if size > 0:
			self.size = size
			# Seed: random initialization
			self.grid = np.random.random(size*size).reshape((size, size)).round()
		else:
			assert None, "Must specify at least one of size, grid, or live_cells"
		print(f'Starting state:\n{self}')


	def __eq__(self, obj):
		return isinstance(obj, State) and self.grid == obj.grid

	def __str__(self):
		s = ' |\n| '.join([' '.join(map(lambda x: '*' if x else ' ', self.grid[i])) for i in range(self.size)])
		return '| ' + s + ' |'

	def update(self, born_cells, died_cells):
		for x,y in born_cells:
			self.grid[x][y] = 1
		for x,y in died_cells:
			self.grid[x][y] = 0

	def find_size(self, live_cells):
		flattened = []
		for x,y in live_cells:
			flattened.extend([x,y])
		return flattened.sort()[-1]

	def living_cells(self):
		"""
		Return (x,y) tuples for living cells for the current state.
		"""
		return [(i,j) for i in range(self.size) for j in range(self.size) if self.grid[i][j] == 1]

class Rules:
	def step(self, state):
		pass

	def step(self, state):
		new_live = []
		new_dead = []
		for i in range(state.size):
			for j in range(state.size):
				live, die = rule(i, j, state)
				if live:
					new_live.append((i,j))
				if die:
					new_dead.append((i,j))
		state.update(new_live, new_dead)
		return state

class StandardRules(Rules):
	"""
	Note that this class is stateless, but using a class allows us to define
	different games if we choose.

	Rules implemented here:
	Any live cell with fewer than two live neighbours dies, as if by underpopulation.
	Any live cell with two or three live neighbours lives on to the next generation.
	Any live cell with more than three live neighbours dies, as if by overpopulation.
	Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
	"""
	def step(self, state):
		"""
		Perform a game step, starting with the passed-in state and returning
		the updated state
		"""
		new_live = []
		new_dead = []
		g=state.grid
		s=state.size
		for i in range(s):
			for j in range(s):
				# We wrap at boundaries: when k-1=-1, that wraps itself;
				# for k+1=state.size, we mod it (which works for -1, too)
				# For simplicity, we count the cell itself, then subtact it
				num_live = sum([state.grid[i2%s][j2%s] for i2 in [i-1,i,i+1] for j2 in [j-1,j,j+1]]) - g[i][j]
				if g[i][j] == 1:
					if num_live < 2 or num_live > 3:
						new_dead.append((i,j))
				elif num_live == 3:
					new_live.append((i,j))
		# We have to wait until the end to update the state.
		state.update(new_live, new_dead)
		return state

def main():
	import argparse
	parser = argparse.ArgumentParser(description="Conway's Game of Life")
	parser.add_argument('--size', metavar='N', type=int, default=100, nargs='?',
	    help='The size of the square grid for the game')
	parser.add_argument('--steps', metavar='N', type=int, default=500, nargs='?',
	    help='The number of steps to run')
	parser.add_argument('--pause', metavar='D', type=float, default=0.0, nargs='?',
	    help='The pause between steps, in seconds')

	args = parser.parse_args()
	print(f"""
Conway's Game of Life:
  Grid size:           {args.size}
  Number steps:        {args.steps}
  Pause between steps: {args.pause}
""")

	def print_state(n, state):
		print(f'\nstate #{n}:\n{state}')

	state = State(size = args.size)
	rules = StandardRules()
	game  = Game(state=state, rules=rules)
	grids = game.run(max_steps = args.steps, pause = args.pause, foreach_state=print_state)
	print(f'\nTook {len(grids)-1} steps.')
	print(game.state)
	print(f'living cells: {game.state.living_cells()}')

if __name__ == "__main__":
    main()
