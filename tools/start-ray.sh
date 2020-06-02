#!/usr/bin/env bash

# It turns out that running this script with no options in a Jupyter notebook cell
# does not properly start Ray. Therefore, notebook cells should use
#   !.../tools/start-ray.sh --check --verbose
# It will
help() {
	cat <<EOF
Check if Ray is already running on the current node. If not start it as the head node.
Usage: $0 [-h|--help] [-c|--check|--check-only] [-v|--verbose]
Where:
	-h|--help                 Print this message and exit
	-c|--check|--check-only   Only check if Ray is running, returning exit code 0 if true, 1 otherwise.
	-v|--verbose              Prints more verbose information, such as how to start Ray if
	                          -c is specified and Ray isn't running.
EOF
}

let check_only=1
let verbose=1
while [[ $# -gt 0 ]]
do
	case $1 in
		-h|--help)
			help
			exit 0
			;;
		-c|--check*)
			let check_only=0
			;;
		-v|--verbose*)
			let verbose=0
			;;
		*)
			echo "ERROR: Unexpected argument $1"
			help
			exit 1
			;;
	esac
	shift
done

verbose_running() {
	cat <<EOF
Ray already running.
EOF
}

verbose_check() {
	cat <<EOF

Ray is not running. Run $0 with no options in a terminal window to start Ray.

EOF
}

verbose_started() {
	cat <<EOF
Ray successfully started.
EOF
}

verbose_failed() {
	cat <<EOF

ERROR: Ray failed to start. Please report this issue to academy@anyscale.com."
ERROR: Provide as much information as you can about your setup, any error messages shown, etc."

EOF
}


$NOOP ray stat > /dev/null 2>&1
let status=$?
if [[ $status -eq 0 ]]
then
	[[ $verbose -eq 0 ]] && verbose_running
elif [[ $check_only -eq 0 ]]
then
	 [[ $verbose -eq 0 ]] && verbose_check
else
	$NOOP ray start --head
	let status=$?
	[[ $status -eq 0 ]] && [[ $verbose -eq 0 ]] && verbose_started
	[[ $status -ne 0 ]] && [[ $verbose -eq 0 ]] && verbose_failed
fi
exit $status
