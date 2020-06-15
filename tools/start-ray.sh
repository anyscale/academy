#!/usr/bin/env bash

# It turns out that running this script with no options in a Jupyter notebook cell
# does not properly start Ray. Therefore, notebook cells should use
#   !.../tools/start-ray.sh --check --verbose
# It will tell you what to do if Ray isn't running.
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
INFO: Ray is already running.
EOF
}

start_terminal="You can start a terminal in Jupyter. Click the "+" under the "Edit" menu."

verbose_check() {
	cat <<EOF

INFO: Ray is not running. Run $0 with no options in a terminal window to start Ray.
INFO: ($start_terminal)

EOF
}

verbose_started() {
	cat <<EOF
INFO: Ray successfully started!
EOF
}

verbose_failed() {
	cat <<EOF

ERROR: Ray failed to start. Please report this issue to academy@anyscale.com."
ERROR: Provide as much information as you can about your setup, any error messages shown, etc."

EOF
}

verbose_multiple() {
	cat <<EOF

ERROR: Multiple instances of Ray are running:
ERROR:   $@
ERROR: This probably means that one or more notebooks or shell scripts we started Ray incorrectly.
ERROR:
ERROR:    **** Please report this bug to academy@anyscale.com ****
ERROR:
ERROR: To fix this issue, use the following steps:
ERROR:
ERROR: 1. Run "ray stop" SEVERAL TIMES in a terminal window.
ERROR:    ($start_terminal)
ERROR: 2. Run "ray start --head" in the terminal window.
ERROR: 3. Try rerunning the cell that ran this script. If it now prints the following,
ERROR:    everything is okay:

	INFO: Ray is already running.

ERROR: If it still throws the same error, then do these steps and try again:
ERROR:
ERROR: 1. Save your work in any other open notebooks.
ERROR: 2. Close all the other notebooks.
ERROR: 3. Shut down their kernels using the Jupyter tab on the left-hand side that shows the
ERROR:    running kernels.
ERROR: 4. Rerun the "ray stop" and "ray start --head" commands.

EOF
}

# Hack to determine if there are multiple running instances.
find_multiple_instances() {
	$NOOP ray stat 2>&1 | grep 'ConnectionError: Found multiple' | while read line
	do
		echo $line | sed -e 's/^.*{\([^}]*\)}.*$/\1/'
	done
}
check_multiple_instances() {
	instances=$(find_multiple_instances)
	[[ -n $instances ]] && echo $instances && return 1
	return 0
}

$NOOP ray stat > /dev/null 2>&1
let status=$?
if [[ $status -eq 0 ]]
then
	[[ $verbose -eq 0 ]] && verbose_running
else # error status returned. Determine why, then handle.
	instances=$(check_multiple_instances)
	let status=$?
	if [[ $status -ne 0 ]]
	then
		# Always print these messages
		verbose_multiple $instances
	elif [[ $check_only -eq 0 ]]
	then
		[[ $verbose -eq 0 ]] && verbose_check
	else
		$NOOP ray start --head
		let status=$?
		# Always print these messages
		[[ $status -eq 0 ]] && verbose_started
		[[ $status -ne 0 ]] && verbose_failed
	fi
	exit $status
fi
