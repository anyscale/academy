#!/usr/bin/env bash

expected_conda_env=tensorflow_p36

help() {
	cat <<EOF
Complete setup of the Jupyter Lab environment.
Usage: $0 [-h|--help]
Where:
	-h | --help        Print this message and exit
EOF
}

while [[ $# -gt 0 ]]
do
	case $1 in
		-h|--help)
			help
			exit 0
			;;
		*)
			echo "ERROR: Unexpected argument $1"
			help
			exit 1
			;;
	esac
	shift
done

JUPYTER=/home/ubuntu/anaconda3/bin/jupyter
extensions=( @pyviz/jupyterlab_pyviz )

echo "Adding extensions to Jupyter Lab, as needed:"
for ext in "${extensions[@]}"
do
	echo "extension: $ext"
	$NOOP $JUPYTER labextension check --installed "$ext" || $JUPYTER labextension install "$ext"
done

$JUPYTER labextension  update --all
$JUPYTER lab build

echo "All extensions:"
$NOOP $JUPYTER labextension list
