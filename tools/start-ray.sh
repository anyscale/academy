#!/usr/bin/env bash

help() {
	cat <<EOF
Check if Ray is already running on the current node. If not start it as the head node.
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

ray stat > /dev/null 2>&1 || ray start --head
