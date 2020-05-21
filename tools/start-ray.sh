#!/usr/bin/env bash

help() {
	cat <<EOF
Check if Ray is already running on the current node. If not start it as the head node.
Usage: $0 [-h|--help] [-c|--check|--check-only]
Where:
	-h|--help                 Print this message and exit
	-c|--check|--check-only   Only check if Ray is running, returning exit code 0 if true, 1 otherwise.
EOF
}

check_only=
while [[ $# -gt 0 ]]
do
	case $1 in
		-h|--help)
			help
			exit 0
			;;
		-c|--check*)
			check_only=true
			;;
		*)
			echo "ERROR: Unexpected argument $1"
			help
			exit 1
			;;
	esac
	shift
done

if [[ -n $check_only ]]
then
	ray stat > /dev/null 2>&1
else
	ray stat > /dev/null 2>&1 || ray start --head
	if [[ $? -eq 0 ]]
	then
		echo
		echo "Ray already running or successfully started"
	else
		echo
		echo "ERROR: Ray failed to start. Please report this issue to academy@anyscale.com."
		echo "ERROR: Provide as much information as you can about your setup, any error messages shown, etc."
	fi
fi

