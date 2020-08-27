
# Make the Docker image: Edit the tags as appropriate.
# NOTE: Assumes the git repo has a tagged release already.

: ${GIT_TAG:=v1.8.1-RC1}
: ${DOCKER_IMAGE_TAG:=1.8.1}
: ${ORGANIZATION:=anyscale}
: ${DOCKERFILE:=docker/Dockerfile}

help() {
	cat <<EOF
$0 [GIT_TAG=tag] [ACADEMY_VERSION=tag] [DOCKER_IMAGE_TAG=tag] [ORGANIZATION=org] [make_args]

where:
-h | --help         Print this message and quit.
GIT_TAG             The tagged release in GitHub for the Academy
ACADEMY_VERSION     What Academy version string to use. Default: GIT_TAG without 'v'.
DOCKER_IMAGE_TAG    Tag for the created Docker image. Default: ACADEMY_VERSION
ORGANIZATION        Organization for the image, especially for uploading. Default: anyscale
make_args           Flags for make or targets to build. Default: "all", which builds
                    "docker_image docker_upload". Upload requires Docker Hub account credentials.

TIPS: Use make's "-n" flag to echo commands without running them.
EOF
}

for arg in "$@"
do
	case $arg in
		-h|--help)
			help
			exit 0
			;;
	esac
done

$NOOP make \
  GIT_TAG=$GIT_TAG DOCKER_IMAGE_TAG=$DOCKER_IMAGE_TAG \
  ORGANIZATION=$ORGANIZATION DOCKERFILE=$DOCKERFILE "$@"
