#!/usr/bin/env bash

expected_conda_env=tensorflow_p36

conda_env=$(conda info | grep 'active environment' | sed -e 's/^[^:]*: *//g')
if [[ $conda_env = 'base' ]] || [[ $conda_env = 'None' ]]
then
	# Only do these steps if the user is not already in a non-base environment
	echo "Activating $expected_conda_env conda environment"
	source $HOME/anaconda3/etc/profile.d/conda.sh
	conda activate $expected_conda_env
fi

echo "Node.js required for some Jupyter Lab extensions. Installing..."
conda install -y nodejs

echo "Adding extensions to Jupyter Lab:"
for ext in @jupyter-widgets/jupyterlab-manager @pyviz/jupyterlab_pyviz @bokeh/jupyter_bokeh
do
	echo "$ext"
	jupyter labextension install "$ext"
done
echo "All extensions:"
jupyter labextension list

echo "Running jupyter lab build:"
jupyter lab build
