
# Make the Docker images: Edit the tags as appropriate.
# NOTE: Assumes the git repo has a tagged release already.

: ${DOCKERFILE_BASE:=docker/Dockerfile}

help() {
	cat <<EOF
$0 [-h|--help] [definitions] [make_args]

where:
-h | --help         Print this message and quit.

The "definitions" are the following, where NAME="value1 value2" syntax is required:

GIT_TAG             The tagged release in GitHub for the Academy. REQUIRED ARGUMENT
ACADEMY_VERSION     What Academy version string to use. Default: GIT_TAG without 'v'.
DOCKER_TAGS         Tags for the created Docker images. Default: ACADEMY_VERSION
ORGANIZATION        Organization for the images, used when uploading to Docker Hug.
                    Default: anyscale
DOCKERFILE_BASE     The base name of the Docker files. Default: $DOCKERFILE_BASE

make_args           Flags passed to 'make' or targets to build. Default: "all", which
                    builds and uploads the images. Uploading requires that you have
                    logged into your Docker Hub account ahead of time!

For example, to create two Docker images from git tag v1.2.3 with Docker tags
1.2.3 and latest, use this:

$0 GIT_TAG=v1.2.3 DOCKER_TAGS="1.2.3 latest"

TIP: Pass "-n" to tell make to echo commands without running them.
EOF
}

error() {
	echo "ERROR: $@"
	help
	exit 1
}

MAKE_ARGS=()
git_tag_seen=
while [[ $# -gt 0 ]]
do
	case $1 in
		-h|--help)
			help
			exit 0
			;;
		GIT_TAG*)
			git_tag_seen=yes
			MAKE_ARGS+=("$1")
			;;
		*)
			MAKE_ARGS+=("$1")
			;;
	esac
	shift
done

[[ -z $git_tag_seen ]] && error "GIT_TAG=v123 argument required!"

echo make "${MAKE_ARGS[@]}"
$NOOP make "${MAKE_ARGS[@]}"
