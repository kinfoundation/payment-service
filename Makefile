all:
	trap 'kill %1; kill %2' SIGINT; make run & make worker & make watcher

split: 
	tmux new-session 'make run' \; split-window 'make worker' \; split-window 'make watcher' \;

run:
	. ./local.sh && . ./secrets/.secrets && pipenv run gunicorn -b localhost:5000 payment.app:app

worker:
	. ./local.sh && . ./secrets/.secrets && pipenv run rq worker

watcher:
	. ./local.sh && . ./secrets/.secrets && pipenv run python watcher.py

shell:
	. ./local.sh && . ./secrets/.secrets && pipenv run ipython

run-prod:
	. ./local.sh && . ./secrets/.secrets && gunicorn -b localhost:3000 payment.app:app

worker-prod:
	. ./local.sh && . ./secrets/.secrets && rq worker --url $$APP_REDIS

watcher-prod:
	. ./local.sh && . ./secrets/.secrets && python3 watcher.py

install-prod:
	pipenv run pip freeze > requirements.txt
	pip3 install requirements.txt


# docker related
revision := $(shell git rev-parse --short HEAD)
image := "kinecosystem/payment-service"

build-image:
	docker build -t ${image} -f Dockerfile \
		--build-arg BUILD_COMMIT="${revision}" \
		--build-arg BUILD_TIMESTAMP="$(shell date -u +"%Y-%m-%dT%H:%M:%SZ")" .
	docker tag ${image} ${image}:${revision}

push-image:
	docker push ${image}:latest
	docker push ${image}:${revision}

up:
	. ./local.sh && . ./secrets/.secrets && docker-compose up

generate-funding-address:
	. ./local.sh && docker-compose -f docker-compose.tests.yaml run generate-funding-address


.PHONY: build-image push-image up generate-funding-address shell run run-prod install-prod
