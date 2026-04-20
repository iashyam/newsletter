.PHONY: build up down logs shell clean

# Use 'docker compose' (v2) which is the modern standard and avoids 
# compatibility issues with older 'docker-compose' (v1) versions.
COMPOSE = docker compose

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

shell:
	$(COMPOSE) exec web bash

clean:
	$(COMPOSE) down --volumes --remove-orphans
	docker image rm newsletter-web:latest || true
