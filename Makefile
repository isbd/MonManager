
build:
	docker compose build --no-cache

up:
	docker compose up -d

down:
	docker compose down

refresh: build up

logs:
	docker compose logs -f

seed-types:
	docker compose exec api python seeds/seed_types.py

db-types:
	docker compose exec db psql -U monuser -d mondb -c "SELECT a.name AS attacker, d.name AS defender, e.multiplier FROM type_effectiveness e JOIN types a ON a.id = e.attacker_id JOIN types d ON d.id = e.defender_id ORDER BY a.name;"

db-command:
	docker exec -it monserver_db psql -U monuser -d mondb