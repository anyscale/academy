from bokeh.plotting import figure, show, output_file
from bokeh.models import Band, ColumnDataSource, Range1d
from bokeh.models.tools import HoverTool
import bokeh.io
import numpy as np


# Draw a line and/or a band. At least one must be specified.
# No line?, then pass y_col=None.
# No band?, then pass upper_col=None and lower_col=None
def plot_optional_line_with_optional_band(df, x_col, y_col=None, lower_col=None, upper_col=None,
    title='', x_axis_label='', y_axis_label=''):

    include_band, min_col, max_col = (False, y_col, y_col)
    if upper_col and lower_col:
        include_band, min_col, max_col = (True, lower_col, upper_col)
    include_line = True if y_col else False
    assert include_band or include_line, 'Must specify a band and/or a line data column.'

    y_min=df[min_col].min()
    y_max=df[max_col].max()
    padding=(y_max-y_min)*0.02
    y_min=y_min-padding
    y_max=y_max+padding

    source = ColumnDataSource(df.reset_index())

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
    plot = figure(tools=TOOLS, plot_width=800, plot_height=500, y_range=Range1d(y_min,y_max))

    if include_line:
        plot.scatter(x=x_col, y=y_col, line_color='blue', source=source, size=3, fill_alpha=0.3)
        plot.line(   x=x_col, y=y_col, line_color='black', source=source, line_width=1)

    if include_band:
        # Apparently,you can't just use Band without a line, so when we aren't plotting
        # the line, we need to plot the boundaries of the band as lines.
        if not include_line:
            plot.line(x=x_col, y=lower_col, source=source, line_color='grey', line_width=1)
            plot.line(x=x_col, y=upper_col, source=source, line_color='grey', line_width=1)

        band = Band(base=x_col, lower=lower_col, upper=upper_col, source=source, level='underlay',
                    fill_alpha=0.3, line_width=1, line_color='blue')
        plot.add_layout(band)

    if include_line:
        hover = HoverTool()
        hover.tooltips = [
            (x_col, "$x"),
            (y_col, "$y")]
        plot.add_tools(hover)

    plot.title.text = title
    plot.xgrid[0].grid_line_alpha=0.5
    plot.ygrid[0].grid_line_alpha=0.5
    plot.xaxis.axis_label = x_axis_label
    plot.yaxis.axis_label = y_axis_label

    show(plot)

# Really just a short-hand alias for plot_optional_line_with_optional_band, where
# the line and band are both plotted:
def plot_line_with_min_max(df, x_col, y_col, min_col, max_col, title='', x_axis_label='', y_axis_label=''):
    plot_optional_line_with_optional_band(df, x_col, y_col, lower_col=min_col, upper_col=max_col,
        title=title, x_axis_label=x_axis_label, y_axis_label=y_axis_label)

def plot_line(df, x_col='x', y_col='y', title='', x_axis_label='', y_axis_label=''):
    plot_optional_line_with_optional_band(df, x_col, y_col, lower_col=None, upper_col=None,
        title=title, x_axis_label=x_axis_label, y_axis_label=y_axis_label)

def plot_line_with_stddev(df, x_col, y_col, stddev_col, title='', x_axis_label='', y_axis_label=''):
    df['lower'] = df[y_col] - df[stddev_col]
    df['upper'] = df[y_col] + df[stddev_col]
    plot_optional_line_with_optional_band(df, x_col, y_col, lower_col='lower', upper_col='upper',
        title=title, x_axis_label=x_axis_label, y_axis_label=y_axis_label)

# Used for plotting a space between low and high points, but not a line in the middle.
def plot_between_lines(df, x_col, lower_col, upper_col, title='', x_axis_label='', y_axis_label=''):
    plot_optional_line_with_optional_band(df, x_col, y_col=None, lower_col=lower_col, upper_col=upper_col,
        title=title, x_axis_label=x_axis_label, y_axis_label=y_axis_label)
