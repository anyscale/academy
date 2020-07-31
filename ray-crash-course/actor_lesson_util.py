# Convenience utilities for plotting with Holoviews and Bokeh, and
# running Game of Life experiments. It assumes the data comes in a [x,y,z],
# where z is the life status, 0 for dead, and 1+ for living.

# Tip: For help on `Holoviews` types, enter, e.g.,
# `hv.help(hv.Points)` in a cell.

import time
from math import ceil
import ray
import numpy as np
import pandas as pd

import holoviews as hv
from holoviews import dim, opts
from holoviews.streams import Pipe, Buffer
from holoviews.plotting.util import process_cmap

hv.extension('bokeh')

# A custom color map created at https://projects.susielu.com/viz-palette
default_cmap=["#ffd700",
"#ffb14e",
"#fa8775",
"#ea5f94",
"#cd34b5",
"#9d02d7",
"#0000ff"]
# Alternative, built-in choices from Bokeh:
# default_cmap = 'RdYlBu' # 'Turbo' 'YlOrBr'

default_max_cell_age = 8
default_use_fixed_cell_sizes = True
default_bgcolor = 'white' # '#f6f7dc'
default_game_size = 100
default_plot_size = 800

def fixed_cell_size(plot_size, game_size):
    return round(plot_size/(2*game_size))

def show_cmap(cmap=default_cmap, min_index=0, max_index=default_max_cell_age):
    ls = np.linspace(min_index, max_index, max_index)
    # Use -ls so the "oldest" color is on top.
    xyz = np.c_[-ls, -ls, -ls]
    points = hv.Image(xyz, vdims='z', bounds=(0, min_index, 1, max_index))
    points.opts(cmap=cmap, xaxis=None, ylabel='age', colorbar=False, toolbar=None, title=f'Color Map: {cmap}')
    return points

timing_fmt = 'Total time for {:d} games, {:5d} steps, {:5d} batch size: {:6.3f} seconds'

def new_game_of_life_graph(game_size, plot_size,
                           bgcolor=default_bgcolor, cmap=default_cmap,
                           use_fixed_cell_sizes=default_use_fixed_cell_sizes,
                           max_cell_age=default_max_cell_age):
    """
    The input points will be [x,y,z]. For plotting, we clip z to be no larger
    than max_cell_age. That affects how many colors are chosen from the specified
    color palette. A smaller value of max_cell_size produces faster changes, since
    most lifetimes are low, except for large game sizes, where some patterns can
    be semi-permanent. If use_fixed_cell_sizes=False, then the points grow in size
    from zero (dead) to the clipped size. The log(z)+1 is calculated as an alternative
    for mapping to colors and sizes, but it doesn't work that well for small
    lifetimes. See comment below inline.
    """
    def new_points(data):
        data2 = data
        if len(data) > 0:
            x = np.array(data[0])
            y = np.array(data[1])
            z = np.array(data[2])
            data2 = np.c_[x, y, z, np.log1p(z), np.clip(z, 0, max_cell_age)]
        return hv.Points(data2, kdims=['x', 'y'], vdims=['z', 'z_log1p', 'z_clipped'])

    pipe = Pipe(data=[])
    dmap = hv.DynamicMap(new_points, streams=[pipe])
    cell_sizes = 'z_clipped'  # or use z_log1p or even try z.
    if use_fixed_cell_sizes:
        cell_sizes = fixed_cell_size(plot_size, game_size)
    dmap.opts(
        color='z_clipped', # or use z_log1p or z.
        xlim=(0, game_size), ylim=(0, game_size),
        size=cell_sizes, width=plot_size, height=plot_size,
        bgcolor=bgcolor, cmap=cmap)
    return dmap

# NOTE: Doesn't work well if there's only one graph. It shinks the graph
# to a small size. That's why both the gridspace and graphs list are returned.
# So, when you have only one graph, evaluate graphs[0], not gridspace, in a
# cell to render it.
def new_game_of_life_grid(game_size=10, plot_size=100, x_grid=1, y_grid=1, shrink_factor=1.0,
                          bgcolor=default_bgcolor, cmap=default_cmap,
                          use_fixed_cell_sizes=default_use_fixed_cell_sizes,
                          max_cell_age=default_max_cell_age):
    small_plot_size = round(plot_size/shrink_factor)
    graphs = []
    for _ in range(x_grid * y_grid):
        graphs.append(new_game_of_life_graph(game_size, small_plot_size,
                                             bgcolor=bgcolor, cmap=cmap,
                                             use_fixed_cell_sizes=use_fixed_cell_sizes,
                                             max_cell_age=max_cell_age))
    gridspace = hv.GridSpace(group='Games', kdims=['i', 'j'])
    for i in range(x_grid):
        for j in range(y_grid):
            gridspace[i,j] = graphs[i+j]  # put the dmap in the grid
    return gridspace, graphs

# Graphs can be None when no graphing is being done.
def run_games(games, graphs, steps, batch_size=1, pause_between_batches=0.0):
    if graphs != None:
        assert len(games) == len(graphs), f'Must have the same number of games and graphs: {len(games)} != {len(graphs)}'
    start = time.time()
    num_games = len(games)
    num_batches = int(steps/batch_size)
    for n in range(num_batches):
        time.sleep(pause_between_batches)
        for i in range(num_games):
            pipe = graphs[i].streams[0] if graphs else None
            new_states = games[i].step(batch_size) # batch_size states in list
            for state in new_states:
                xs, ys, zs = state.living_cells() # Do this work even if we don't graph it.
                if pipe != None:
                    pipe.send((xs, ys, zs))
    duration = time.time()-start
    message = timing_fmt.format(num_games, steps, batch_size, duration)
    print(message)
    return num_games, steps, batch_size, duration

# Lots of duplication with run_games, but it's hard to remove if we
# want to use ray.wait().
# Graphs can be None when no graphing is being done.
def run_ray_games(game_actors, graphs, steps, batch_size=1, pause_between_batches=0.0):
    if graphs != None:
        assert len(game_actors) == len(graphs), f'Must have the same number of games and graphs: {len(game_actors)} != {len(graphs)}'
    start = time.time()
    num_games = len(game_actors)
    num_batches = int(steps/batch_size)
    for n in range(num_batches):
        time.sleep(pause_between_batches)
        all_state_ids = [game_actors[i].step.remote(batch_size) for i in range(num_games)]
        still_working = all_state_ids.copy()
        while len(still_working) > 0:
            finished, still_working = ray.wait(still_working, timeout=1.0)
            # We need to match each returned state with the corresponding graph
            indices = [all_state_ids.index(id) for id in finished]
            new_states_finished = ray.get(finished) # a list of batch_size lists
            for i in range(len(new_states_finished)):
                new_states = new_states_finished[i] # a batch_size list
                pipe = graphs[indices[i]].streams[0] if graphs else None
                for state in new_states:
                    xs, ys, zs = state.living_cells() # Do this work even if we don't graph it.
                    if pipe != None:
                        pipe.send((xs, ys, zs))
    duration = time.time()-start
    message = timing_fmt.format(num_games, steps, batch_size, duration)
    print(message)
    return num_games, steps, batch_size, duration
