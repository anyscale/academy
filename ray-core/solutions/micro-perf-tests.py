#!/usr/bin/env python

import numpy as np
import time

# This script tests three diffent implementations of live_neighbors.
# Typical results:
#   live1: mean =  0.02519, stddev =  0.00182
#   live2: mean =  0.04241, stddev =  0.00313
#   live3: mean =  0.03943, stddev =  0.00305
# So live1 is the fastest and also has the lowest standard deviation
# between runs, typically.
# The live* implementations are adapted from Ex4-GameOfLife.py

def live1(i, j, size, grid):
	im1 = i-1 if i > 0      else size-1
	ip1 = i+1 if i < size-1 else 0
	jm1 = j-1 if j > 0      else size-1
	jp1 = j+1 if j < size-1 else 0
	return grid[im1][jm1] + grid[im1][j] + grid[im1][jp1] + grid[i][jm1] + grid[i][jp1] + grid[ip1][jm1] + grid[ip1][j] + grid[ip1][jp1]

def live2(i, j, size, grid):
	return sum([grid[i2%size][j2%size] for i2 in [i-1,i,i+1] for j2 in [j-1,j,j+1]]) - grid[i][j]

def live3(i, j, size, grid):
	im1 = i-1 if i > 0      else size-1
	ip1 = i+1 if i < size-1 else 0
	jm1 = j-1 if j > 0      else size-1
	jp1 = j+1 if j < size-1 else 0
	i2s = [im1,i,ip1]
	j2s = [jm1,j,jp1]
	return sum([grid[i2][j2] for i2 in i2s for j2 in j2s]) - grid[i][j]

def make_grid(size=100):
	return np.random.randint(2, size = size*size).reshape((size, size))

def p(prefix, values, print_values=False):
	mean = np.mean(values)
	stddev = np.std(values)
	fmt = '{:s}: mean = {:8.5f}, stddev = {:8.5f} (values = {:})'
	vals = values if print_values else ['...']
	print(fmt.format(prefix, mean, stddev, vals))

def trial(num_runs, grid_size, print_values = False):
	lives = [live1, live2, live3]
	times = np.zeros((3,num_runs))
	for run in range(num_runs):
		grid = make_grid(grid_size)
		for l in range(3):
			start_time = time.time()
			[lives[l](i, j, grid_size, grid) for i in range(grid_size) for j in range(grid_size)]
			times[l][run] = time.time() - start_time
	for l in range(3):
		p(f'{lives[l]}', times[l], print_values)

def main():
	import argparse
	parser = argparse.ArgumentParser(description="Micro Perf Tests")
	parser.add_argument('--runs', metavar='N', type=int, default=100, nargs='?',
		help='The number of runs (100 or more recommended)')
	parser.add_argument('--size', metavar='N', type=int, default=100, nargs='?',
		help='The size of the square grid')
	parser.add_argument('--values', help='Print the values for each run',
    	action='store_true')

	args = parser.parse_args()
	print(f"""
Micro Perf Tests:
  Runs:                {args.runs}
  Grid size:           {args.size}
  Print runs:          {args.values}
""")
	begin = time.time()
	trial(args.runs, args.size, args.values)
	print('Total time: {:8.5f}'.format(time.time() - begin))

if __name__ == "__main__":
	main()