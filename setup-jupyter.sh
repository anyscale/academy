#!/usr/bin/env bash

echo "Adding extensions to Jupyter Lab:"
for ext in @jupyter-widgets/jupyterlab-manager @pyviz/jupyterlab_pyviz @bokeh/jupyter_bokeh
do
	echo "$ext"
	jupyter labextension install "$ext"
done
echo "All extensions:"
jupyter labextension list
