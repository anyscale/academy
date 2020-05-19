#!/usr/bin/env bash

# What's expected in an Anyscale cluster (at this time)
expected_conda_env=tensorflow_p36

conda_env=$(conda info | grep 'active environment' | sed -e 's/^[^:]*: *//g')
if [[ $conda_env = 'base' ]] || [[ $conda_env = 'None' ]]
then
	# Only do these steps if the user is not already in a non-base environment
	# We don't specifically expect $expected_conda_env, because the actual
	# environment may be different.
	echo "Activating $expected_conda_env conda environment"
	source $HOME/anaconda3/etc/profile.d/conda.sh
	conda activate $expected_conda_env
fi

echo "Node.js required for some Jupyter Lab extensions. Installing if necessary..."
conda install -y nodejs

extensions=(
	@pyviz/jupyterlab_pyviz
#	@jupyter-widgets/jupyterlab-manager
#	@bokeh/jupyter_bokeh
)
echo "Checking or adding extensions to Jupyter Lab:"
for ext in "${extensions[@]}"
do
	echo "extension: $ext"
	jupyter labextension check --installed "$ext" || jupyter labextension install "$ext"
done
echo "All extensions:"
jupyter labextension list

# Should be redundant:
# echo "Running jupyter lab build:"
# jupyter lab build
