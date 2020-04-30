# Convenience utilities for plotting with Holoviews and Bokeh, and
# running Game of Life experiments.

# Tip: For help on `Holoviews` types, enter, e.g.,
# `hv.help(hv.Points)` in a cell.

import time
import holoviews as hv
from holoviews import opts
from holoviews.streams import Pipe, Buffer
import ray

hv.extension('bokeh')

timing_fmt = 'Total time for {:d} games, {:5d} steps, {:5d} batch size: {:6.3f} seconds'

def new_game_of_life_graph(game_size, plot_size):
    pipe = Pipe(data=[])
    dmap = hv.DynamicMap(hv.Points, streams=[pipe])
    cell_size = round(plot_size/(2*game_size))
    dmap.opts(color='Grey', xlim=(0, game_size), ylim=(0, game_size),
        size=cell_size, width=plot_size, height=plot_size)
    return dmap

# NOTE: Doesn't work well if there's only one graph. It shinks the graph
# to a small size. That's why both the gridspace and graphs list are returned.
# So, when you have only one graph, evaluate graphs[0], not gridspace, in a
# cell to render it.
def new_game_of_life_grid(game_size, plot_size, x_grid, y_grid, shrink_factor):
    small_plot_size = round(plot_size/shrink_factor)
    graphs = [new_game_of_life_graph(game_size, small_plot_size) for _ in range(x_grid * y_grid)]
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
            pipe = graphs[i].streams[0] if graphs != None else None
            new_states = games[i].step(batch_size) # batch_size states in list
            for state in new_states:
                xs, ys = state.living_cells() # Do this work even if we don't graph it.
                if pipe != None:
                    pipe.send((xs, ys))
    message = timing_fmt.format(num_games, steps, batch_size, time.time()-start)
    print(message)

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
                pipe = graphs[indices[i]].streams[0] if graphs != None else None
                for state in new_states:
                    xs, ys = state.living_cells() # Do this work even if we don't graph it.
                    if pipe != None:
                        pipe.send((xs, ys))
    message = timing_fmt.format(num_games, steps, batch_size, time.time()-start)
    print(message)
