# Build the Docker image and push to DockerHub, if successful.

# Run with:
#   make GIT_TAG=1.2.3 [other_defs] [options] [targets]
#
# The GIT_TAG argment is mandatory. It can optionally have the
# prefix "v", i.e., v1.2.3, in which case the v will be removed
# when used as a Docker image tag.
#
# Several other variable overrides are optional:
#   DOCKER_IMAGE_TAG      defaults to GIT_TAG with the "v" removed.
#   ORGANIZATION          defaults to anyscale.
#
# WARNING: The Ray version is hard-coded in docker/Dockerfile. Edit as required.

ACADEMY_VERSION      ?= $(GIT_TAG:v%=%)
DOCKER_IMAGE_TAG     ?= $(ACADEMY_VERSION)

ORGANIZATION         ?= anyscale

all: echo docker_make docker_upload

echo:
	@echo "Academy Git tag:      $(GIT_TAG)"
	@echo "Docker image tag:     $(DOCKER_IMAGE_TAG)"
	@echo "Organization:         $(ORGANIZATION)"

check_tag:
ifndef ACADEMY_VERSION
	@echo "GIT_TAG (for this repo) must be defined, e.g., GIT_TAG=v1.2.3 make ..."
	exit 1
endif

docker_make: check_tag stage_academy
	docker build \
		--tag $(ORGANIZATION)/academy:$(DOCKER_IMAGE_TAG) \
		--tag $(ORGANIZATION)/academy:latest \
		--build-arg VERSION=$(ACADEMY_VERSION) \
		-f docker/Dockerfile stage

stage_academy: stage/academy-$(ACADEMY_VERSION)

stage/academy-$(ACADEMY_VERSION):
	@rm -rf stage
	@mkdir -p $@
	@curl -o stage/academy-$(ACADEMY_VERSION).zip --location \
		https://github.com/anyscale/academy/archive/$(GIT_TAG).zip
	@cd stage/; unzip academy-$(ACADEMY_VERSION).zip

docker_upload: check_tag docker_login
	docker push $(ORGANIZATION)/academy:$(DOCKER_IMAGE_TAG)

docker_login:
	docker login --username $(USER)
