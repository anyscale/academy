import math, statistics, random, time, sys
import numpy as np
import pandas as pd
import ray

import time
import holoviews as hv
from holoviews import opts
from holoviews.streams import Counter, Tap
from bokeh_util import square_circle_plot, two_lines_plot, means_stddevs_plot
hv.extension('bokeh')

from bokeh.layouts import gridplot, layout
from bokeh.models import Slider, Button
from bokeh.plotting import figure, output_file, show

from pi_calc import MonteCarloPi, compute_pi_for


DEFAULT_NS = [1000, 10000, 100000]
DEFAULT_RADIUS = 1.0
DEFAULT_BOUNDS = (-DEFAULT_RADIUS, -DEFAULT_RADIUS, DEFAULT_RADIUS, DEFAULT_RADIUS)
DEFAULT_MIN_N = 100
DEFAULT_MAX_N = 100000
DEFAULT_N_PER_PI_CALC = DEFAULT_MIN_N
DEFAULT_PLOT_SIZE = 1200
DEFAULT_IMAGE_SIZE = round(DEFAULT_PLOT_SIZE/2)
DEFAULT_CMAP = 'Spectral'
DEFAULT_IMAGE_COLOR_IDX = 2
DEFAULT_POINT_COLOR_IDX = 125
DEFAULT_PI_UPDATE_FORMAT = 'Pi ~= {:8.7f}\nerror = {:6.3f}%\nn = {:d}\n(N ~ {:d})'

img_opts = opts.Image(cmap=DEFAULT_CMAP, toolbar=None,
                    height=DEFAULT_PLOT_SIZE, width=DEFAULT_PLOT_SIZE,
                    xaxis=None, yaxis=None)

def make_circle(radius=DEFAULT_RADIUS):
    def circle(t):
        return (radius*np.sin(t), radius*np.cos(t), t)
    lin = np.linspace(-np.pi, np.pi, 200)
    return hv.Path([circle(lin)]).opts(img_opts).opts(line_width=2, color='red')

def make_rect(bounds=DEFAULT_BOUNDS, color='blue'):
    minX, minY, maxX, maxY = bounds
    return hv.Path([(minX, minY), (maxX, minY), (maxX, maxY), (minX, maxY), (minX, minY)]).opts(
        img_opts).opts(line_width=2, color='blue')

def make_text(content):
    return hv.Text(0, 0, content).opts(img_opts).opts(
        toolbar=None, height=100, width=150, xaxis=None, yaxis=None,
        text_alpha=1.0, bgcolor='lightgrey')

def make_image(data=None, image_size=DEFAULT_IMAGE_SIZE, bounds=DEFAULT_BOUNDS, color_idx=DEFAULT_IMAGE_COLOR_IDX, label='Pi:'):
    if data == None:
        data = np.full((image_size, image_size), color_idx, dtype=np.uint8)
    return hv.Image(data, label=label, bounds=bounds).opts(img_opts)

def to_pixel(array, image_size=DEFAULT_IMAGE_SIZE):
    """
    NumPy array input for real coordinates. Returns image pixel index.
    To keep indices between 0, inclusize, and image_size, exclusive, we set the upper bound to image_size - 1
    """
    array2 = (array+1.0)/2.0 # Shift to origin range between (0-1,0-1)
    return np.rint((image_size-1)*array2).astype(int)  # Scale to pixels

def make_overlay(items, width=DEFAULT_PLOT_SIZE, height=DEFAULT_PLOT_SIZE):
    return hv.Overlay(items=items).opts(width=width, height=height)


def make_update(k, N, counter_instance,
    n_per_pi_calc=DEFAULT_N_PER_PI_CALC, pi_update_format=DEFAULT_PI_UPDATE_FORMAT):
    """Returns a closure used as the update function for a dmap."""
    pi_calc = MonteCarloPi()
    image = make_image()
    rect = make_rect()
    circle = make_circle()
    text = make_text('Pi calculation')
    def update(counter):
        """
        Due to an apparent bug in Holoview's ``periodic`` class for
        DynamicMaps, the update gets called far more than the specified
        ``count`` value in ``run_simulations`` below. Unfortunately, we
        can't just "ignore" extra invocations (if we've already computed
        N values), because we have to return an overlay and there
        appears to be no reliable way to save the last one(?). That's
        why we call ``counter_instance.clear()``, which removes the
        dmap as a subscriber.
        """
        def updated_image(value, xys, img):
            xs,  ys  = xys[:,0], xys[:,1]
            pxs, pys = to_pixel(xs), to_pixel(ys)
            for i in range(pxs.size):
                img.data[pxs[i]][pys[i]] = value
            return img

        pi, count_inside, count_total, xys_in, xys_out = pi_calc.sample(n_per_pi_calc)
        error = 100.0*abs(pi - math.pi)/math.pi
        label = pi_update_format.format(pi, error, count_total, N)

        img1 = updated_image(1, xys_in, image)
        img2 = updated_image(0, xys_out, img1)
        img3 = hv.Image(img2, label=label)
        text = make_text(label)
        overlay = make_overlay(items=[img3, rect, circle, text])
        if count_total >= N:
            counter_instance.clear()  # basically stop further updates.
        return overlay
    return update

def make_dmaps(Ns = DEFAULT_NS):
    dmaps = []
    for k in range(len(Ns)):
        N = Ns[k]
        counter = Counter(transient=True)
        psize = int(DEFAULT_PLOT_SIZE/len(Ns))
        dmap_update = make_update(k, N, counter)
        dmap = hv.DynamicMap(dmap_update, streams=[counter]).opts(height=psize, width=psize)
        # We fetch DEFAULT_N_PER_PI_CALC points each pass through "update", so only count up to N/...
        dmaps.append(dmap)
    return dmaps

def run_simulations(dmaps, Ns = DEFAULT_NS, n_per_pi_calc=DEFAULT_N_PER_PI_CALC):
    for i in range(len(dmaps)):
        dmaps[i].periodic(0.01, count=int(Ns[i]/n_per_pi_calc)-1, block=False)

def stop_simulations(dmaps):
    [dmap.periodic.stop() for dmap in dmaps]

if __name__ == '__main__':

    dmaps = make_dmaps(DEFAULT_NS)
    show(dmaps[0] + dmaps[1] + dmaps[2])
    run_simulations(dmaps)

