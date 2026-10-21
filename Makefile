.PHONY: up down logs build restart api-shell smoke

up:
	docker compose --env-file .env up --build -d

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

build:
	docker compose build

restart:
	docker compose restart

api-shell:
	docker compose exec api bash

smoke:
	curl -sf http://localhost:8000/health && echo " api ok"
	curl -sf http://localhost:3000 >/dev/null && echo " web ok"
