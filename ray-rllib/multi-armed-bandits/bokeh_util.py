from bokeh.plotting import figure, show, output_file
from bokeh.models import Band, ColumnDataSource, Range1d
import bokeh.io
import numpy as np

def plot_cumulative_regret(df):
    df['lower'] = df['mean'] - df['std']
    df['upper'] = df['mean'] + df['std']
    ymin=df['lower'].min()
    ymax=df['upper'].max()

    source = ColumnDataSource(df.reset_index())

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
    p = figure(tools=TOOLS, y_range=Range1d(ymin,ymax))

    p.scatter(x='num_steps_trained', y='mean', line_color='black', fill_alpha=0.3, size=5, source=source)
    band = Band(base='num_steps_trained', lower='lower', upper='upper', source=source, level='underlay',
                fill_alpha=0.3, line_width=1, line_color='blue')
    p.add_layout(band)

    p.title.text = "Cumulative Regret"
    p.xgrid[0].grid_line_alpha=0.5
    p.ygrid[0].grid_line_alpha=0.5
    p.xaxis.axis_label = 'Training Steps'
    p.yaxis.axis_label = 'Regret'

    show(p)

def plot_model_weights(means, covs):
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