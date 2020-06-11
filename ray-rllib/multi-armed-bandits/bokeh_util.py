from bokeh.plotting import figure, show, output_file
from bokeh.models import Band, ColumnDataSource, Range1d
import bokeh.io
import numpy as np


# TODO: remove duplication with between the plot_* functions.
def plot_line(df, x_col='x', y_col='y', title='', x_axis_label='', y_axis_label=''):
    source = ColumnDataSource(df.reset_index())

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
    p = figure(tools=TOOLS, plot_width=800, plot_height=500)

    p.scatter(x=x_col, y=y_col, line_color='blue',  source=source, size=3, fill_alpha=0.3)
    p.line(   x=x_col, y=y_col, line_color='black', source=source, line_width=2)

    p.title.text = title
    p.xgrid[0].grid_line_alpha=0.5
    p.ygrid[0].grid_line_alpha=0.5
    p.xaxis.axis_label = x_axis_label
    p.yaxis.axis_label = y_axis_label

    show(p)

def plot_line_with_stddev(df, x_col, y_col, stddev_col, title='', x_axis_label='', y_axis_label=''):
    df['lower'] = df[y_col] - df[stddev_col]
    df['upper'] = df[y_col] + df[stddev_col]
    ymin=df['lower'].min()
    ymax=df['upper'].max()

    source = ColumnDataSource(df.reset_index())

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
    p = figure(tools=TOOLS, plot_width=800, plot_height=500, y_range=Range1d(ymin,ymax))

    p.scatter(x=x_col, y=y_col, line_color='black', source=source, size=3, fill_alpha=0.3)
    p.line(   x=x_col, y=y_col, line_color='black', source=source, line_width=2)
    band = Band(base=x_col, lower='lower', upper='upper', source=source, level='underlay',
                fill_alpha=0.3, line_width=1, line_color='blue')
    p.add_layout(band)

    p.title.text = title
    p.xgrid[0].grid_line_alpha=0.5
    p.ygrid[0].grid_line_alpha=0.5
    p.xaxis.axis_label = x_axis_label
    p.yaxis.axis_label = y_axis_label

    show(p)

# Used for plotting a space between low and high points, but not a line in the middle.
def plot_between_lines(df, x_col, lower_col, upper_col, title='', x_axis_label='', y_axis_label=''):
    source = ColumnDataSource(df.reset_index())

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
    p = figure(tools=TOOLS, plot_width=800, plot_height=500)

    band = Band(base=x_col, lower=lower_col, upper=upper_col, source=source,
                fill_alpha=1.0, line_width=2, line_color='blue')
    p.add_layout(band)

    p.title.text = title
    p.xgrid[0].grid_line_alpha=0.5
    p.ygrid[0].grid_line_alpha=0.5
    p.xaxis.axis_label = x_axis_label
    p.yaxis.axis_label = y_axis_label

    show(p)

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
