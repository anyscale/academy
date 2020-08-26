
# Make the Docker image: Edit the tags as appropriate.
# NOTE: Assumes the git repo has a tagged release already.

make GIT_TAG=v1.8.0 DOCKER_IMAGE_TAG=1.8.0 ORGANIZATION=anyscale "$@"
