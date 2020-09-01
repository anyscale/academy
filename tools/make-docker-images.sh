#!/usr/bin/env zsh

# Make the Docker images: Edit the tags as appropriate.
# NOTE: Assumes the git repo has a tagged release already.

: ${DOCKERFILE_BASE:=docker/Dockerfile}
script=$0

help() {
	cat <<EOF
$script [-h|--help] [--docker|--docker-tag tag ...] [--org|--organization org] git_tag [make_args]

Builds two docker images "organization/academy-base:tag" and "organization/academy-all:tag"

where:
-h | --help                  Print this message and quit.
--docker | --docker-tag tag  Build images with this tag. Zero or more allowed.
                             Default: git_tag minus the leading "v", if any.
--org | --organization org   Use this organization, as in "org/academy-all:tag".
                             Default: anyscale
git_tag                      The tagged release in GitHub for the Academy. REQUIRED ARGUMENT.
--git|--git-tag git_tag      Alternative way of specifing the required Git tag.
make_args                    Flags and targets passed to 'make' or targets to build.
                             Default: "all", which builds and uploads the images, along with
                             Makefile variable definitions driven by the other options for this
                             script. Uploading (docker push) requires that you have already
                             logged into the Docker Hub account corresponding to the organization
                             ahead of time!

The following environment variables can be passed, too, as part of make-args.
The syntax NAME="value1 value2" is required:

ACADEMY_VERSION     What Academy version string to use. Embedded in the Docker images.
                    Default: GIT_TAG without 'v'.
DOCKERFILE_BASE     The base name of the Docker files. Default: $DOCKERFILE_BASE
                    to which the strings "-base" and "-all" will be appended to find
                    the corresponding docker files for the two images.

For example, to create but not upload two Docker images from git tag v1.2.3 with Docker tags
1.2.3 and latest, with a different docker file "base" use this:

$script --docker-tag 1.2.3 --docker-tag latest v1.2.3 DOCKERFILE_BASE=test/Dockerfile docker-images

TIP: Pass "-n" to tell make to echo commands without running them.
EOF
}

error() {
	echo "ERROR: $@"
	help
	exit 1
}

GIT_TAG=
DOCKER_TAGS=()
MAKE_ARGS=()
ORGANIZATION=anyscale
while [[ $# -gt 0 ]]
do
	case $1 in
		-h|--help)
			help
			exit 0
			;;
		--git*)
			shift
			GIT_TAG="$1"
			;;
		--docker*)
			shift
			DOCKER_TAGS+=("$1")
			;;
		--org*)
			shift
			ORGANIZATION="$1"
			;;
		*)
			if [[ -z $GIT_TAG ]]
			then
				GIT_TAG=$1
			else
				MAKE_ARGS+=("$1")
			fi
			;;
	esac
	shift
done

[[ -z $GIT_TAG ]] && error "The Git tag argument is required!"
[[ ${#DOCKER_TAGS} -gt 0 ]] && DOCKER_TAGS_ARG=DOCKER_TAGS="${DOCKER_TAGS}"
$NOOP make GIT_TAG="$GIT_TAG" "$DOCKER_TAGS_ARG" ORGANIZATION="$ORGANIZATION" ${MAKE_ARGS}
