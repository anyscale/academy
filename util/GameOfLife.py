import numpy as np
import time

def print_grid(n, grid):
	print(f'{n}:\n{grid}')


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

	def run(self, max_steps = 1000, foreach_grid = print_grid, pause=0.0):
		"""
		Run the game for max_steps iterations, pausing pause seconds.

		Args:
			max_steps (int) the number of iterations
			foreach_grid (function) a function(n,grid) to which each new grid is passed.
			pause (float) the number of seconds between iterations (default: 0)
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
			self.state = self.rules.step(self.state)
			foreach_grid(i, self.state.grid)
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
			rng = np.random.default_rng()
			self.grid = rng.integers(2, size=(self.size, self.size))
		else:
			assert None, "Must specify at least one of size, grid, or live_cells"
		print(f'Starting grid:\n{self.grid}')


	def __eq__(self, obj):
		return isinstance(obj, State) and self.grid == obj.grid

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
		Return (x,y) tuples for living cells
		"""
		return living_cells_from_grid(self.grid)

	def living_cells_from_grid(self, grid):
		"""
		Return (x,y) tuples for living cells

		Args:
			grid (NxN array)  if None, use the state's grid.
		"""
		return [(i,j) for i in range(self.size) for j in range(self.size) if grid[i][j] == 1]

class Rules:
	def step(self, state):
		pass

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
	def __init__(self):
		self.deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

	def step(self, state):
		new_live = []
		new_dead = []
		for i in range(state.size):
			for j in range(state.size):
				num_live = self.find_live_neighbours(i, j, state)
				if state.grid[i][j] == 1:
					if num_live < 2 or num_live > 3:
						new_dead.append((i,j))
				elif num_live == 3:
						new_live.append((i,j))
		state.update(new_live, new_dead)
		return state

	def find_live_neighbours(self, i, j, state):
		num_live = 0
		for (idelta, jdelta) in self.deltas:
			i2 = self.mod(i+idelta, state.size)
			j2 = self.mod(j+jdelta, state.size)
			num_live += state.grid[i2][j2]
		return num_live

	def mod(self, index, size):
		if index < 0:
			index = size - 1
		elif index == size:
			index = 0
		return index

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

	state = State(size = args.size)
	rules = StandardRules()
	game  = Game(state=state, rules=rules)
	grids = game.run(max_steps = args.steps, pause = args.pause)
	print(f'n = {len(grids)}')
	print(grids[-1])
	print(game.state.living_cells())

if __name__ == "__main__":
    main()
