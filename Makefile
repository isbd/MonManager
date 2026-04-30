
build:
	docker compose build --no-cache

up:
	docker compose up -d

down:
	docker compose down

refresh: build up

logs:
	docker compose logs -f

db-command:
	docker exec -it monserver_db psql -U monuser -d mondb