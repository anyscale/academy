# Build the Docker iamge and push to DockerHub, if successful.

# Run with TAG=1.2.3 make ... I
# If you pass a string like v1.2.3, the v will be removed.

TAG := $(TAG:v%=%)

all: check_tag docker_make docker_login docker_upload

echo:
	@echo "Using Version $(TAG)"

check_tag:
ifndef TAG
	@echo "TAG must be defined, e.g., TAG=1.2.3 make ..."
	exit 1
endif

docker_make:
	docker build --tag anyscale/academy:$(TAG) -f docker/Dockerfile .

docker_login:
	docker login --username $(USER)

docker_upload:
	docker push anyscale/academy:$(TAG)
