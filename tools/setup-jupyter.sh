#!/usr/bin/env bash

expected_conda_env=tensorflow_p36

help() {
	cat <<EOF
Complete setup of the Jupyter Lab environment.
Usage: $0 [-h|--help] [-e|--env ENV]
Where:
	-h | --help        Print this message and exit
	-e | --env  ENV    Use this Conda environment (default: $expected_conda_env)
EOF
}

while [[ $# -gt 0 ]]
do
	case $1 in
		-h|--help)
			help
			exit 0
			;;
		-e|--env)
			shift
			expected_conda_env=$1
			;;
		*)
			echo "ERROR: Unexpected argument $1"
			help
			exit 1
			;;
	esac
	shift
done

# What's expected in an Anyscale cluster (at this time)

conda_env=$(conda info | grep 'active environment' | sed -e 's/^[^:]*: *//g')
if [[ $conda_env != $expected_conda_env ]]
then
	$NOOP source $HOME/anaconda3/etc/profile.d/conda.sh
	echo "running: conda activate $expected_conda_env"
	$NOOP conda activate $expected_conda_env
fi

echo "Node.js required for some Jupyter Lab extensions. Installing if necessary..."
$NOOP conda install -y nodejs

extensions=( @pyviz/jupyterlab_pyviz )

echo "Adding extensions to Jupyter Lab, as needed:"
for ext in "${extensions[@]}"
do
	echo "extension: $ext"
	$NOOP jupyter labextension check --installed "$ext" || jupyter labextension install "$ext"
done
echo "All extensions:"
$NOOP jupyter labextension list
