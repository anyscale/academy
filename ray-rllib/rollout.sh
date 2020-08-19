#!/usr/bin/env bash
script=$0
error() {
    echo "ERROR: $@"
    exit 1
}

default_pattern='CartPole.*checkpoint-20$'
help() {
    cat <<EOF
$script: Run rllib rollout on a checkpoint.
Usage: $script [-h|--help] [-c|--checkpoint-pattern c] [other_rllib_options]

Where:

-h | --help                   Print this message and quit.
-c | --checkpoint-pattern c   Match on this directory name regex pattern. Default is "$default_pattern" and search is done in ~/ray_projects
other_rllib_options           Any other arguments for the "rllib" command. They must come after the other arguments.

EOF
}

pattern="$default_pattern"
while [ $# -gt 0 ]
do
    case $1 in 
        -h|--h*)
            help
            exit 0
            ;;
        -c|--c*)
            shift
            pattern="$1"
            ;;
        *)
            break
            ;;
    esac
    shift        
done

checkpoint_dirs=( $(find ~/ray_results | egrep "$pattern" | sort))
[[ ${#checkpoint_dirs} -eq 0 ]] && error "No directories matching pattern \"$pattern\" found in ~/ray_results!"
if [[ ${#checkpoint_dirs} -gt 1 ]]
then
    echo "Found more than one 'checkpoint-20' directory:"
    for d in "${checkpoint_dirs[@]}"; do echo "  $d"; done
    echo "Using the last one:"
fi

checkpoint_dir="${checkpoint_dirs[${#checkpoint_dirs[@]}-1]}"
echo "running: rllib rollout $checkpoint_dir --run PPO $@"
$NOOP rllib rollout $checkpoint_dir --run PPO "$@"
