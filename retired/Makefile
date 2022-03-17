# Build the Docker image and push to DockerHub, if successful.

# Run with:
#   make GIT_TAG=1.2.3 [other_defs] [options] [targets]
#
# The GIT_TAG argment is mandatory. It can optionally have the
# prefix "v", i.e., v1.2.3, in which case the v will be removed
# when used as a Docker image tag.
#
# Several other variable overrides are optional:
#   ORGANIZATION       defaults to anyscale.
#   DOCKER_TAGS        Defaults to GIT_TAG with the "v" removed.
#   LATEST_TAG         Defaults to "latest". Define it to be EMPTY
#                      if you DON'T want an image with tag "latest".
#
# WARNING: The Ray version is hard-coded in docker/Dockerfile*. Edit as required.

ORGANIZATION         ?= anyscale
ACADEMY_VERSION      ?= $(GIT_TAG:v%=%)
DOCKER_TAGS          ?= $(ACADEMY_VERSION)

DOCKERFILE_BASE      := docker/Dockerfile
IMAGE_SUFFIXES       := base all
IMAGE_NAMES          := $(IMAGE_SUFFIXES:%=academy-%)

staged_name := academy-$(ACADEMY_VERSION)

all: docker-images docker-upload
docker-images: academy-base-image  academy-all-image    # build both images
docker-upload: academy-base-upload academy-all-upload   # upload both images
academy-base:  academy-base-image  academy-base-upload  # build and upload base image
academy-all:   academy-all-image   academy-all-upload   # build and upload all image

echo:
	@echo "Academy Git tag:    $(GIT_TAG)"
	@echo "Docker image tags:  $(DOCKER_TAGS)"
	@echo "Organization:       $(ORGANIZATION)"

check-tag:
ifndef ACADEMY_VERSION
	@echo "GIT_TAG (for this repo) must be defined, e.g., GIT_TAG=v1.2.3 make ..."
	exit 1
endif

academy-all-image: echo check-tag stage-academy  # check tag and staging only for "all"
academy-base-image: echo stage-base
$(IMAGE_NAMES:%=%-image): echo
	docker build \
		$(DOCKER_TAGS:%=--tag $(ORGANIZATION)/${@:%-image=%}:%) \
		--build-arg VERSION=$(ACADEMY_VERSION) \
		--build-arg ORGANIZATION=$(ORGANIZATION) \
		-f $(DOCKERFILE_BASE)-${@:%-image=%} stage

stage-base: stage/academy-base
	cp environment-docker.yml $<

stage-academy: stage/academy-all/$(staged_name).zip stage/academy-all/$(staged_name)
$(IMAGE_NAMES:%=stage/%):
	mkdir -p $@

stage/academy-all/$(staged_name).zip: stage/academy-all/
	@rm -rf stage/academy-all/*
	@curl -o stage/academy-all/$(staged_name).zip --fail-early --location \
		https://github.com/anyscale/academy/archive/$(GIT_TAG).zip

stage/academy-all/$(staged_name):
	@cd stage/academy-all/; unzip $(staged_name).zip || ( \
	  echo && echo "***** Invalid Zip file??? *****" && \
	  echo "Look at the contents of stage/academy-all/$(staged_name).zip. Did you specify a valid tag, e.g., 'v' in v1.2.3??" && \
	  rm -rf stage/* && exit 1 )
	@echo "Staged Academy: stage/academy-all/$(staged_name)"

# Commented out dependency on docker-login, because it prompts you every time, even if
# you have already logged in.
$(IMAGE_NAMES:%=%-upload): echo check-tag # docker-login
	@for tag in $(DOCKER_TAGS); do \
	  echo "docker push $(ORGANIZATION)/${@:%-upload=%}:$$tag"; \
	  docker push $(ORGANIZATION)/${@:%-upload=%}:$$tag; \
	done

docker-login:
	docker login --username $(USER)
