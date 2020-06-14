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
ERROR: This probably means that one or more notebooks started Ray incorrectly, in addition
ERROR: to running this $0 script that should be used instead.
ERROR:
ERROR:    **** Please report this bug to academy@anyscale.com ****
ERROR:
ERROR: To clean up now, go to the other notebook tabs. For each one, add and run a new code
ERROR: cell with the following statement:

	ray.shutdown()

ERROR: Then try running this cell again. If it now prints the following, everything is okay:

	INFO: Ray is already running.

ERROR: However, if it still prints that multiple instances of ray are running (this message!),
ERROR: then do the following steps:
ERROR: 1. Run "ray stop" SEVERAL TIMES in a terminal window.
ERROR:    ($start_terminal)
ERROR: 2. Close all the other notebooks.
ERROR: 3. Shutdown their kernels using the Jupyter tab on the left-hand side that shows the
ERROR:    running kernels.
ERROR: Once these steps are done, then rerun the previous cell to check again. Follow
ERROR: the instructions that will be printed to start Ray.

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
