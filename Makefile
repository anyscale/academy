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
#   DOCKERFILE            defaults to docker/Dockerfile.
#
# WARNING: The Ray version is hard-coded in docker/Dockerfile*. Edit as required.

ACADEMY_VERSION      ?= $(GIT_TAG:v%=%)
DOCKER_IMAGE_TAG     ?= $(ACADEMY_VERSION)
ORGANIZATION         ?= anyscale
DOCKERFILE           ?= docker/Dockerfile

staged_name := academy-$(ACADEMY_VERSION)

all: docker_image docker_upload

echo:
	@echo "Academy Git tag:      $(GIT_TAG)"
	@echo "Docker image tag:     $(DOCKER_IMAGE_TAG)"
	@echo "Organization:         $(ORGANIZATION)"

check_tag:
ifndef ACADEMY_VERSION
	@echo "GIT_TAG (for this repo) must be defined, e.g., GIT_TAG=v1.2.3 make ..."
	exit 1
endif

docker_image: check_tag echo stage_academy
	docker build \
		--tag $(ORGANIZATION)/academy:$(DOCKER_IMAGE_TAG) \
		--tag $(ORGANIZATION)/academy:latest \
		--build-arg VERSION=$(ACADEMY_VERSION) \
		-f $(DOCKERFILE) stage

stage_academy: stage/$(staged_name)

stage/$(staged_name): stage/$(staged_name).zip
	@cd stage/; unzip $(staged_name).zip || ( \
	  echo && echo "***** Invalid Zip file??? *****" && \
	  echo "Look at the contents of stage/$(staged_name).zip. Did you specify a valid tag, e.g., 'v' in v1.2.3??" && \
	  rm -rf stage/* && exit 1 )
	@echo "Staged Academy: stage/$(staged_name)"

stage/$(staged_name).zip:
	@mkdir -p stage
	@rm -rf stage/*
	@curl -o stage/$(staged_name).zip --fail-early --location \
		https://github.com/anyscale/academy/archive/$(GIT_TAG).zip

docker_upload: check_tag echo docker_login
	docker push $(ORGANIZATION)/academy:$(DOCKER_IMAGE_TAG)
	docker push $(ORGANIZATION)/academy:latest

docker_login:
	docker login --username $(USER)
