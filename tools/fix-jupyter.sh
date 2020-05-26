#!/usr/bin/env bash

JUPYTER=

help() {
	cat <<EOF
$0: Complete setup of the Jupyter Lab environment.

Usage: $0 [-h|--help] [-j|--jupyter path_to_jupyter]
Where:
	-h | --help                     Print this message and exit
	-j | --jupyter path_to_jupyter  Specific jupyter instance.
	                                Default: output of "which jupyter"
EOF
}

error() {
	echo "ERROR: $@"
	echo
	echo "Help:"
	help
	exit 1
}

while [[ $# -gt 0 ]]
do
	case $1 in
		-h|--h*)
			help
			exit 0
			;;
		-j|--j*)
			shift
			JUPYTER="$1"
			;;
		*)
			echo "ERROR: Unexpected argument $1"
			help
			exit 1
			;;
	esac
	shift
done

echo "jupyter: $JUPYTER"
[[ -n "$JUPYTER" ]] || JUPYTER=$(which jupyter) || error "command 'which jupyter' failed! Is it installed?"
[[ -x "$JUPYTER" ]] || error "Jupyter not found or not executable: $JUPYTER"

extensions=( @pyviz/jupyterlab_pyviz )

echo "Adding extensions to Jupyter Lab, as needed:"
for ext in "${extensions[@]}"
do
	echo "extension: $ext"
	$NOOP $JUPYTER labextension check --installed "$ext" || $JUPYTER labextension install "$ext"
done

$NOOP $JUPYTER labextension update --all
$NOOP $JUPYTER lab build

echo "All extensions:"
$NOOP $JUPYTER labextension list
