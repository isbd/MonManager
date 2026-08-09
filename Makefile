
.PHONY: help build up down refresh lint lint-check db-command logs nuke seed client client-lint

build-clean: ## Build the containers fresh
	docker compose build --no-cache

build: ## Build the containers
	docker compose build

db-command: ## Enter postgres container for SQL commands
	docker exec -it monserver_db psql -U monuser -d mondb

down: ## Shut the docker containers down
	docker compose down

lint: ## Linting fixes to the api directory
	docker exec -it monserver_api sh -c "ruff check --fix . && ruff format ."

lint-check: ## Check for linting issues without fixes
	docker exec -it monserver_api ruff check .

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk -F '##' '{printf "%-15s %s\n", $$1, $$2}'

logs: ## View the logs from the docker containers
	docker compose logs -f

nuke: ## Nuke the database and re-seed it
	@read -p "Are you sure? Type 'yes' to continue: " r; \
		[ "$$r" = "yes" ] || exit 1
	$(MAKE) up
	docker exec -it monserver_db psql -U monuser -d mondb -c \
		"DROP SCHEMA public CASCADE; \
		CREATE SCHEMA public;"
	$(MAKE) down
	$(MAKE) refresh
	$(MAKE) seed

refresh-clean: ## Build the containers fresh then restart them
	$(MAKE) build-clean
	$(MAKE) up

refresh: ## Build the containers then restart them
	$(MAKE) build
	$(MAKE) up

seed: ## Seed the data into the database
	$(MAKE) -C seed seed

up: ## Bring the docker containers up
	docker compose up -d

# Emulator

CLIENT ?= 1
ID     ?= $(CLIENT)
WIDTH  ?= 51
HEIGHT ?= 19

ifdef POCKET
WIDTH  := 26
HEIGHT := 20
endif

client-build: ## Build the craftos client image
	docker compose -f docker-compose.client.yml build craftos

client-lint:
	docker run --rm -v "$(CURDIR)":/code:z -w /code \
	  --user "$$(id -u):$$(id -g)" \
	  pipelinecomponents/luacheck:latest \
	  --config /code/.luacheckrc client

client: ## Start a client (CLIENT=2, POCKET=1, or WIDTH=n HEIGHT=n)
	@xhost +SI:localuser:root >/dev/null
	docker stop monmanager-craftos-$(CLIENT) 2>/dev/null || true
	docker rm monmanager-craftos-$(CLIENT) 2>/dev/null || true
	CRAFTOS_ID=$(ID) CRAFTOS_WIDTH=$(WIDTH) CRAFTOS_HEIGHT=$(HEIGHT) \
	docker compose -f docker-compose.client.yml run --rm -it \
		--name monmanager-craftos-$(CLIENT) craftos
	@xhost -SI:localuser:root >/dev/null

pocket: ## Shortcut for a pocket-sized client
	@$(MAKE) client POCKET=1

kill-clients: ## Kills all craftos client containers
	docker kill $$(docker ps -q --filter "name=monmanager-craftos-*")
