from bokeh.plotting import figure, show, output_file
from bokeh.models import Band, ColumnDataSource, Range1d
import bokeh.io
import numpy as np
import sys

sys.path.append('../..')
from util.line_plots import plot_line_with_stddev

def plot_cumulative_regret(df):
    plot_line_with_stddev(df,
        x_col='num_steps_trained', y_col='mean', stddev_col='std',
        title='Cumulative Regret', x_axis_label='step', y_axis_label='cumulative regret')

def plot_wheel_bandit_model_weights(means, covs):
    # markers = ["asterisk", "circle", "diamond", "square", "x"]
    colors  = ["blue", "black", "green", "red", "yellow"]
    labels  = ["arm{}".format(i) for i in range(5)]

    tooltips = [
        ("name", "$name"),
        ("array size", "$x"),
        ("time", "$y")]

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
    p = figure(tools=TOOLS, tooltips=tooltips, match_aspect=True)

    for i in range(0, 5):
        x, y = np.random.multivariate_normal(means[i] / 30, covs[i], 5000).T
        p.scatter(x=x, y=y, size=2,
                  color=colors[i], marker='circle', legend_label=labels[i], name=labels[i])

    p.title.text = "Weight distributions of arms"
    p.xgrid[0].grid_line_alpha=0.5
    p.ygrid[0].grid_line_alpha=0.5

    show(p)
