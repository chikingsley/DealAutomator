.PHONY: up down logs test shell clean

up:
	docker-compose up --build -d

down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	docker-compose run --rm app pytest

shell:
	docker-compose run --rm app /bin/bash

clean:
	docker-compose down -v
