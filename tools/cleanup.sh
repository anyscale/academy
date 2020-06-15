#!/usr/bin/env bash

help() {
	cat <<EOF
Lists temporary files generated during the lessons that you might want to remove to save space,
but doesn't them.
Usage: $0 [-h|--help] [-v|--verbose]
Where:
	-h|--help                 Print this message and exit
	-v|--verbose              Prints more verbose information, such as how to start Ray if
	                          -c is specified and Ray isn't running.
EOF
}

let verbose=1
while [[ $# -gt 0 ]]
do
	case $1 in
		-h|--help)
			help
			exit 0
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

script=$0
info() {
	[[ $verbose -eq 0 ]] && echo && echo "$script: $@"
}

info "Directories and files you might want to delete:"

info "'Temporary' directories:"
find . -type d \( -name 'tmp*' -o -name '*notes*' \)

info "Checkpoint and cache directories:"
for d in *checkpoint* .*checkpoint* *pycache*
do
	[[ -d $d ]] && echo $d
done 2> /dev/null

find [a-z]* -type d \( -name '*checkpoint*' -o -name '*cache' \) | \
egrep -v '(mountain-car|bipedal-walker)-checkpoint'

