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
	[[ $verbose -eq 0 ]] && echo && echo "INFO: $script: $@"
}

info "Directories and files you might want to delete:"

info "'Temporary' directories:"
find . -type d \( -name 'tmp*' -o -name '*notes*' \)

info "Checkpoint, cache, and test-run directories:"
for d in *checkpoint* .*checkpoint* *pycache*
do
	[[ -d $d ]] && echo $d
done 2> /dev/null

find [a-z]* -type d \( -name '*checkpoint*' -o -name '*cache' -o -name 'test-run*' \) | \
grep -v '/tmp/' | egrep -v '(mountain-car|bipedal-walker)-checkpoint'

info "*.txt or *.text (e.g., notes), *.csv, *.tsv, *.json, and other files that you might not want:"
find [a-z]* -type f \( -name '*.txt' -o -name '*.text' -o -name '*.csv' -o -name '*.tsv' -o -name '*.json' \) | \
egrep -v '(tmp/|.ipynb_checkpoints/|images/.*.meta.json|requirements.txt|multi-armed-bandits/market.tsv)'
